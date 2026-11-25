#!/usr/bin/env python3
"""Build offline trial and palette releases, plus a standalone GitHub Pages site."""
import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

from package_release import package, write_member
from palette_catalog import read_catalog, render_page, SOURCE_CREDITS

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "scripts/distribution"


def text_file(path, content):
    path.write_text(content, encoding="utf-8", newline="\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_archive(path, members):
    """Create sorted archives without inheriting host path, timestamp or mode."""
    with ZipFile(path, "x", compression=ZIP_DEFLATED) as archive:
        for name, source in sorted(members.items()):
            write_member(archive, name, source.read_bytes())
    with ZipFile(path) as archive:
        if set(archive.namelist()) != set(members) or archive.testzip():
            raise ValueError(f"Incomplete archive: {path.name}")


def route_table(skill):
    rows = []
    index = skill / "references/figure-family-index.md"
    for line in index.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| V"):
            continue
        key, question, view, condition = (cell.strip() for cell in line.strip("|").split("|"))
        if not re.fullmatch(r"V\d{2}", key):
            raise ValueError(f"Invalid figure route: {key}")
        cells = []
        for cell in (question, view, condition):
            formatted = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="academic-figure/references/\2">\1</a>', escape(cell))
            cells.append(f"<td>{formatted}</td>")
        rows.append(f'<tr id="{key}"><th scope="row">{key}</th>{"".join(cells)}</tr>')
    if not rows:
        raise ValueError("No figure routes in the published guide")
    return rows


def build_trial(stage, output, catalogue):
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[\w.-]+)?", version):
        raise ValueError("Invalid VERSION")
    trial = stage / f"Academic-Figure-Trial-{version}"
    archive = stage / "skill.zip"
    package(ROOT, archive)
    with ZipFile(archive) as bundle:
        bundle.extractall(trial)
    skill = trial / "academic-figure"
    subprocess.run([sys.executable, "-B", str(skill / "scripts/scaffold_project.py"),
                    str(trial / "Statistical-Demo")], check=True, stdout=subprocess.DEVNULL)
    # A trial first opens with the user's installed packages. Opening it merely
    # to inspect data must not bootstrap renv before the environment check.
    text_file(trial / "Statistical-Demo/.Rprofile",
              "# Trial uses installed R packages. See START.html before opting into renv.\n")
    citation = (skill / "CITATION.cff").read_text(encoding="utf-8")
    date = re.search(r"^date-released:\s*(\d{4}-\d{2}-\d{2})\s*$", citation, re.M)
    if not date:
        raise ValueError("Set the release date in CITATION.cff")
    start = (TEMPLATES / "start.html.in").read_text(encoding="utf-8")
    text_file(trial / "START.html", start.replace("{{VERSION}}", version)
              .replace("{{RELEASE_DATE}}", date[1]).replace("{{PALETTE_COUNT}}", str(len(catalogue["palettes"]))))
    rows = route_table(skill)
    routes = (TEMPLATES / "routes.html.in").read_text(encoding="utf-8")
    text_file(trial / "ROUTES.html", routes.replace("{{ROUTE_ROWS}}", "\n".join(rows))
              .replace("{{ROUTE_COUNT}}", str(len(rows))))

    files = {p.relative_to(trial).as_posix(): p for p in trial.rglob("*") if p.is_file()}
    hashes = {rel: sha256(p) for rel, p in sorted(files.items())}
    inner = json.loads((skill / "RELEASE_SHA256.json").read_text(encoding="utf-8"))
    if any(hashes["academic-figure/" + name] != digest for name, digest in inner.items()):
        raise ValueError("Trial contents differ from release manifest")
    manifest = trial / "SHA256SUMS.txt"
    text_file(manifest, "".join(f"{digest}  {rel}\n" for rel, digest in hashes.items()))
    files[manifest.name] = manifest
    write_archive(output / "Academic-Figure-Trial.zip", {trial.name + "/" + rel: p for rel, p in files.items()})


def colour_rows(card):
    selected = set(card["main"] + card["support"])
    extra = [code for code in card["source_colors"] if code not in selected]
    return card["main"], card["support"], extra


def draw_overview(catalogue, output):
    import pymupdf as pdf

    cards = catalogue["palettes"]
    names = ("分组主色", "辅助填充", "原卡其余色值")
    roles = [colour_rows(card) for card in cards]
    ink = (0.13, 0.19, 0.21)
    muted = (0.30, 0.36, 0.38)
    pitch = 54
    left = 20
    first_column = 165
    offsets = []
    x = first_column
    for i in range(len(names)):
        offsets.append(x)
        x += max(max(len(row[i]) for row in roles), 2) * pitch + 12
    width = x + left
    first_row = 97
    row_height = 42
    footer = first_row + len(cards) * row_height + 12
    with pdf.open() as doc:
        page = doc.new_page(width=width, height=footer + 52)

        def label(x, y, value, size, font="china-s", color=ink):
            # The built-in CJK font uses full ems for Latin glyphs. Measure Latin
            # runs with Helvetica so numbers and names keep normal letter spacing.
            if font != "china-s":
                page.insert_text((x, y), value, fontname=font, fontsize=size, color=color)
                return
            for run in re.findall(r"[\x20-\x7e]+|[^\x20-\x7e]+", value):
                family = "helv" if run.isascii() else font
                page.insert_text((x, y), run, fontname=family, fontsize=size, color=color)
                x += pdf.get_text_length(run, fontname=family, fontsize=size)

        label(left, 32, "科研绘图色卡", 21)
        label(left, 54, f'{len(cards)} 套命名组合', 10, color=muted)
        label(left + 95, 54, "Academic Figure   /   Raphael He", 10, "helv", muted)
        label(left, 79, "名称与调用 ID", 9)
        for x, name in zip(offsets, names):
            label(x, 79, name, 9)
        page.draw_line((left, 86), (width - left, 86), color=ink, width=0.7)
        for row, (card, groups) in enumerate(zip(cards, roles)):
            y = first_row + row * row_height
            title = card["name"]
            if card["id"] == catalogue["default_id"]:
                title += "  · 默认"
            label(left, y + 11, title, 10)
            label(left, y + 25, card["id"], 7.8, "cour", muted)
            for x, codes in zip(offsets, groups):
                for col, code in enumerate(codes):
                    at = x + col * pitch
                    rgb = tuple(int(code[i:i+2], 16) / 255 for i in (1, 3, 5))
                    page.draw_rect((at, y, at + 50, y + 16), color=(.79, .80, .80), fill=rgb, width=.3)
                    label(at, y + 26, code, 8, "cour")
            page.draw_line((left, y + 34), (width - left, y + 34), color=(.88, .89, .88), width=.4)
        for i, credit in enumerate(SOURCE_CREDITS):
            label(left, footer + i * 16, credit, 9, color=muted)
        page.get_pixmap(matrix=pdf.Matrix(2.6, 2.6), alpha=False).save(output)


def build(destination):
    destination = destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Choose a new output directory: {destination}")
    if destination.resolve().is_relative_to(ROOT):
        raise ValueError("Choose an output directory outside the repository")
    destination.parent.mkdir(parents=True, exist_ok=True)
    catalogue = read_catalog()
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix=".academic-dist-") as temp:
        stage = Path(temp)
        result = stage / "result"
        site = result / "site"
        site.mkdir(parents=True)
        overview = site / "palettes.png"
        draw_overview(catalogue, overview)
        text_file(site / "index.html", render_page(catalogue, standalone=True, overview=overview.read_bytes()))
        write_archive(result / "Academic-Figure-Palettes.zip", {
            "index.html": site / "index.html", "palettes.png": site / "palettes.png",
        })
        build_trial(stage, result, catalogue)
        archives = sorted(result.glob("*.zip"))
        text_file(result / "SHA256SUMS.txt", "".join(f"{sha256(p)}  {p.name}\n" for p in archives))
        # Reserve the destination exclusively so concurrent builds never replace it.
        destination.mkdir()
        try:
            for artifact in result.iterdir():
                artifact.rename(destination / artifact.name)
        except BaseException:
            shutil.rmtree(destination)
            raise
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="New directory outside the repository")
    args = parser.parse_args()
    try:
        print(build(args.output))
    except ImportError as exc:
        parser.exit(2, f"Missing build dependency: {exc}. Install requirements-qa.txt and retry.\n")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Distribution build failed: {exc}\n")
