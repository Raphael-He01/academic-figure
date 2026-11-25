#!/usr/bin/env python3
"""Reconcile file evidence into an export CSV without promoting full acceptance.

Exit 0: mechanical checks passed; 1: failed check; 2: unavailable/inconclusive.
Paths are relative to --project-root, or inferred from output/qa/manifest.csv;
for other manifest locations their parent is the default root. No network calls.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def run_audit(script: Path, args: list[str]) -> int:
    try:
        result = subprocess.run([sys.executable, '-B', str(script), *args],
                                capture_output=True, text=True, timeout=60)
        return result.returncode if result.returncode in (0, 1, 2) else 2
    except (OSError, subprocess.TimeoutExpired):
        return 2


def reconcile(manifest: Path, project_root: Path | None = None) -> tuple[list[dict], int]:
    manifest = manifest.resolve()
    before = manifest.read_bytes()
    rows = list(csv.DictReader(io.StringIO(before.decode('utf-8-sig'))))
    if not rows or 'path' not in rows[0]:
        raise ValueError('Manifest requires at least one row and a path column')
    if project_root is None:
        project_root = manifest.parents[2] if manifest.parent.name == 'qa' and manifest.parent.parent.name == 'output' else manifest.parent
    project_root = project_root.resolve()
    scripts = Path(__file__).resolve().parent
    codes = []
    for row in rows:
        if not row['path'].strip():
            raise ValueError('Empty export path')
        path = (project_root / row['path']).resolve()
        for key in ('width_mm', 'height_mm'):
            if row.get(key):
                value = float(row[key])
                if not math.isfinite(value) or value <= 0:
                    raise ValueError(f'{key} must be finite and positive')
        current_hash = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ''
        # Human reviews are valid only for the explicitly bound file revision.
        if not current_hash or row.get('review_sha256') != current_hash:
            row['scientific_review'] = 'pending'
            row['visual_review'] = 'pending'
            row['review_sha256'] = ''
        row['file_sha256'] = current_hash
        row['acceptance'] = 'pending'
        row['font_embedding'] = 'not_auditable' if path.suffix.lower() == '.pdf' else 'not_applicable'
        if not current_hash:
            row['file_check'] = 'failed'
            row['acceptance'] = 'failed'
            codes.append(1)
            continue
        args = []
        for key in ('width_mm', 'height_mm'):
            if row.get(key):
                args.extend(['--' + key.replace('_', '-'), row[key]])
        code = run_audit(scripts / 'verify_exports.py', [*args, str(path)])
        row['file_check'] = {0: 'pass', 1: 'failed', 2: 'not_auditable'}[code]
        codes.append(code)
        if path.suffix.lower() == '.pdf':
            code = run_audit(scripts / 'qa/audit_pdf_fonts.py', [str(path), '--json'])
            row['font_embedding'] = {0: 'embedded', 1: 'not_embedded', 2: 'not_auditable'}[code]
            codes.append(code)
        if row['file_check'] == 'failed' or row['font_embedding'] == 'not_embedded':
            row['acceptance'] = 'failed'
    for row in rows:
        export = (project_root / row['path']).resolve()
        after_hash = hashlib.sha256(export.read_bytes()).hexdigest() if export.is_file() else ''
        if after_hash != row['file_sha256']:
            raise ValueError('Export changed during audit; no update written')
    fields = list(dict.fromkeys(key for row in rows for key in row))
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    # A failed probe never leaves a half-written manifest; detect concurrent edits.
    if manifest.read_bytes() != before:
        raise ValueError('Manifest changed during audit; no update written')
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='', dir=manifest.parent,
                                         prefix='.export-audit-', delete=False) as stream:
            tmp = Path(stream.name)
            stream.write(buffer.getvalue())
        os.replace(tmp, manifest)
    finally:
        if tmp and tmp.exists():
            tmp.unlink()
    return rows, 1 if 1 in codes else (2 if 2 in codes else 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--project-root', type=Path)
    args = parser.parse_args()
    try:
        rows, code = reconcile(args.manifest, args.project_root)
        print(json.dumps([{k: row.get(k) for k in ('path', 'file_sha256', 'file_check', 'font_embedding', 'acceptance')} for row in rows], indent=2))
        return code
    except (OSError, ValueError, csv.Error, UnicodeError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
