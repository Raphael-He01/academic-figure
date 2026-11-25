#!/usr/bin/env python3
"""Render or verify a caption from explicitly supplied, formatted facts."""
import argparse
import json
from pathlib import Path
import string
import sys


def render(template, facts):
    if not isinstance(facts, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in facts.items()):
        raise ValueError('facts must be a JSON object of named formatted strings')
    return string.Template(template).substitute(facts)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['render', 'verify'])
    p.add_argument('template', type=Path)
    p.add_argument('facts', type=Path)
    p.add_argument('caption', type=Path)
    args = p.parse_args()
    try:
        text = render(args.template.read_text(encoding='utf-8'), json.loads(args.facts.read_text(encoding='utf-8')))
        if args.mode == 'render':
            with args.caption.open('x', encoding='utf-8') as f:
                f.write(text)
            print('Caption created; scientific review pending.')
            return 0
        if args.caption.read_text(encoding='utf-8') != text:
            print('Caption differs from the current template and facts.', file=sys.stderr)
            return 1
        print('Caption matches supplied facts; scientific review pending.')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'caption error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
