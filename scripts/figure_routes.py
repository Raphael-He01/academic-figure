#!/usr/bin/env python3
"""Find a figure family by ID or words in the bundled Chinese selection guide."""
import argparse
import json
from pathlib import Path

from chart_guard import check, validate_facts

INDEX = Path(__file__).resolve().parents[1] / 'references/figure-family-index.md'
# Only map families whose main chart matches an implemented evidence check.
# Other families may include optional layers with their own prerequisites.
PRIMARY_CHARTS = {
    'V03': 'posterior_pairs',
    'V04': 'weighted_state_field',
    'V06': 'sample_feature_atlas',
    'V08': 'stage_flow',
    'V09': 'contribution_waterfall',
}


def find_routes(query):
    terms = query.casefold().split()
    if not terms:
        raise ValueError('Enter a figure ID or search term.')
    matches = []
    for line in INDEX.read_text(encoding='utf-8').splitlines():
        if line.startswith('| V'):
            fields = [v.strip() for v in line.strip('|').split('|')]
            search_text = ' '.join(fields[:3]).casefold()
            if all(word in search_text for word in terms):
                matches.append(fields)
    return matches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', nargs='+', help='ID or terms, for example V06 or medoid')
    parser.add_argument('--facts', type=Path, help='Check the primary chart against a JSON file of verified boolean facts')
    args = parser.parse_args()
    facts = None
    try:
        rows = find_routes(' '.join(args.query))
        if args.facts is not None:
            facts = json.loads(args.facts.read_text(encoding='utf-8-sig'))
            validate_facts(facts)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    for key, question, view, condition in rows:
        print(f'{key}  {question}\n  {view}\n  {condition}')
        if facts is None:
            continue
        chart = PRIMARY_CHARTS.get(key)
        if chart is None:
            print('  证据：请按本条所列使用条件人工核对。')
            continue
        missing = check(chart, facts)['missing_or_unconfirmed']
        if missing:
            print(f'  证据：{chart} 缺少已确认条件：{", ".join(missing)}')
        else:
            print(f'  证据：{chart} 的显式条件已满足，可进入图稿设计复核。')
    if not rows:
        print('没有匹配的条目。请用研究问题中的关键词或 V01–V32 编号重试。')
    return 0 if rows else 1


if __name__ == '__main__':
    raise SystemExit(main())
