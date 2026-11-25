"""Compare individual paths and stage totals in a synthetic two-desk workflow."""
import csv
from collections import Counter
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
from chart_guard import check, suggest


def compare():
    stages = ('intake', 'review', 'release')
    with (HERE / 'desks.csv').open(newline='', encoding='utf-8') as f:
        records = list(csv.DictReader(f))
    ids = [r['item'] for r in records]
    if not ids or len(set(ids)) != len(ids) or not all(ids):
        raise ValueError('The example requires one row per identified item')
    if any(not row[stage] for row in records for stage in stages):
        raise ValueError('The closed-cohort example requires all three desk assignments')

    totals = {s: Counter(row[s] for row in records) for s in stages}
    changes = []
    for before, after in zip(stages, stages[1:]):
        edges = Counter((r[before], r[after]) for r in records)
        outgoing = Counter()
        incoming = Counter()
        for (origin, destination), n in edges.items():
            outgoing[origin] += n
            incoming[destination] += n
        if outgoing != totals[before] or incoming != totals[after]:
            raise ValueError('Transitions disagree with desk counts')
        changes.append(sum(n for (a, b), n in edges.items() if a != b))

    # The supplied schema defines ordered stages and a flow unit of one item.
    common = {'ordered_stages_confirmed': True, 'flow_unit_confirmed': True}
    tracked = dict(common, transition_links_verified=True, stage_totals_reconciled=True)
    return {'stage_counts': totals, 'items_changing_desk': changes,
            'with_item_paths': suggest(tracked)['candidates'],
            'with_stage_counts_only': check('stage_flow', common)}


if __name__ == '__main__':
    print(json.dumps(compare(), indent=2))
