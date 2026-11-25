#!/usr/bin/env python3
"""Bind figure, data and caption files by SHA-256; does not assess their meaning."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    create = sub.add_parser('create')
    create.add_argument('record', type=Path)
    for name in ('data', 'figure', 'caption'):
        create.add_argument('--' + name, type=Path, required=True)
    verify = sub.add_parser('verify')
    verify.add_argument('record', type=Path)
    args = p.parse_args()
    try:
        if args.command == 'create':
            base = args.record.resolve().parent
            entries = {}
            for key in ('data', 'figure', 'caption'):
                path = getattr(args, key).resolve(strict=True)
                if not path.is_relative_to(base):
                    raise ValueError('all files must be within the evidence record directory')
                entries[key] = {'path': path.relative_to(base).as_posix(), 'sha256': digest(path)}
            with args.record.open('x', encoding='utf-8') as f:
                json.dump({'version': 1, 'files': entries, 'review': 'pending'}, f, indent=2, ensure_ascii=False)
                f.write('\n')
            print('Evidence recorded; scientific and visual review pending.')
            return 0
        record = json.loads(args.record.read_text(encoding='utf-8'))
        if record.get('version') != 1 or set(record['files']) != {'data', 'figure', 'caption'}:
            raise ValueError('invalid evidence record')
        base = args.record.resolve().parent
        changed = []
        for key, item in record['files'].items():
            path = (base / item['path']).resolve(strict=True)
            if not path.is_relative_to(base) or digest(path) != item['sha256']:
                changed.append(key)
        print(json.dumps({'status': 'stale' if changed else 'unchanged', 'changed': changed,
                          'scope': 'File identity only; scientific and visual review remain separate.'}))
        return 1 if changed else 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f'evidence error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
