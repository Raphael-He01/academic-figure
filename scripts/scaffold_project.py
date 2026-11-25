#!/usr/bin/env python3
"""Copy the bundled R-first academic-figure template without overwriting files."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an academic-figure project scaffold; existing files are never overwritten."
    )
    parser.add_argument("destination", type=Path, help="Destination project directory")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    template = Path(__file__).resolve().parents[1] / "assets" / "r-template"
    if not template.is_dir():
        print(f"Template directory is missing: {template}", file=sys.stderr)
        return 2

    destination = args.destination.expanduser().absolute()
    if destination.is_symlink():
        print(f"Refusing a symlinked destination: {destination}", file=sys.stderr)
        return 3
    files = {p.relative_to(template): p for p in sorted(template.rglob("*")) if p.is_file()}
    files[Path("data/palettes/catalog.json")] = template.parent / "palettes/catalog.json"
    files[Path("scripts/check_r_project.R")] = Path(__file__).with_name("check_r_project.R")
    directories = {destination / parent for relative in files for parent in relative.parents}
    ancestor = destination.parent
    while not ancestor.exists() and not ancestor.is_symlink():
        directories.add(ancestor)
        ancestor = ancestor.parent
    conflicts = [path for path in directories if path.is_symlink() or (path.exists() and not path.is_dir())]
    conflicts.extend(target for target in (destination / relative for relative in files)
                     if target.exists() or target.is_symlink())
    if conflicts:
        print("Refusing to overwrite a target or traverse a non-directory:", file=sys.stderr)
        for path in sorted(conflicts):
            print(f"  {path}", file=sys.stderr)
        return 3

    created: dict[Path, os.stat_result] = {}
    try:
        for directory in sorted(directories, key=lambda path: (len(path.parts), path.parts)):
            try:
                directory.mkdir()
            except FileExistsError:
                if directory.is_symlink() or not directory.is_dir():
                    raise
            else:
                created[directory] = directory.lstat()
        for relative, source in files.items():
            target = destination / relative
            with source.open("rb") as reader:
                writer = target.open("xb")
                identity = os.fstat(writer.fileno())
                try:
                    with writer:
                        shutil.copyfileobj(reader, writer)
                finally:
                    # Preserve the original identity even if another process swaps the path.
                    current = target.lstat()
                    if not os.path.samestat(current, identity):
                        raise FileExistsError(f"Destination changed while copying: {target}")
                    created[target] = current
    except BaseException as error:
        for path, before in reversed(created.items()):
            try:
                current = path.lstat()
                if not os.path.samestat(current, before):
                    continue
                if stat.S_ISDIR(before.st_mode):
                    path.rmdir()
                elif (current.st_mtime_ns, current.st_size) == (before.st_mtime_ns, before.st_size):
                    path.unlink()
            except FileNotFoundError:
                pass
            except OSError as cleanup_error:
                print(f"Retained {path}: {cleanup_error}", file=sys.stderr)
        if isinstance(error, OSError):
            print(f"Scaffold copy failed: {error}", file=sys.stderr)
            return 3 if isinstance(error, FileExistsError) else 2
        raise

    print(f"Created academic-figure scaffold at {destination}")
    for relative in files:
        print(f"  {relative}")
    print(f'Open {destination / "Academic-Figure.Rproj"} in RStudio.')
    print('Check the project with source("scripts/check_r_project.R") and check_figure_environment().')
    print('For the example, run source("R/run_example.R") from the project root.')
    print(f'First preview: {destination / "output/previews/academic_figure_example_preview.png"}')
    print('Optional Codex XLSX handoff: ask Codex to run scripts/build_example_workbook.mjs with its bundled Node; then source("R/validate_excel_handoff.R") in the RStudio session.')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
