#!/usr/bin/env python3
"""Check explicit evidence for a proposed plot; never infer facts from column names."""
import json
import sys


REQUIREMENTS = {
    'paired_lines': ('paired_ids_confirmed', 'paired_observations_available'),
    'violin': ('individual_values_available',),
    'error_bars': ('interval_definition_confirmed', 'interval_values_available'),
    'survival_curve': ('event_times_available', 'censoring_confirmed'),
    'posterior_pairs': ('joint_draw_keys_verified', 'two_or_more_parameters_available',
                        'posterior_sampling_confirmed', 'draw_weights_accounted_for'),
    'stage_flow': ('ordered_stages_confirmed', 'transition_links_verified',
                   'flow_unit_confirmed', 'stage_totals_reconciled'),
    'contribution_waterfall': ('additive_definition_confirmed', 'common_additive_scale_confirmed',
                               'baseline_and_total_available', 'contributions_reconciled'),
    'weighted_state_field': ('state_samples_available', 'time_schedule_confirmed',
                             'within_time_weights_verified', 'common_state_bin_edges_confirmed'),
    'sample_feature_atlas': ('sample_feature_values_available', 'sample_ids_verified',
                             'annotation_join_verified', 'feature_scale_confirmed'),
}


def validate_facts(facts):
    if not isinstance(facts, dict) or any(type(v) is not bool for v in facts.values()):
        raise ValueError('facts must be a JSON object containing boolean values')


def missing_facts(chart, facts):
    return [key for key in REQUIREMENTS[chart] if facts.get(key) is not True]


def check(chart, facts):
    validate_facts(facts)
    if chart not in REQUIREMENTS:
        raise ValueError('unsupported chart; manual review required')
    missing = missing_facts(chart, facts)
    return {'chart': chart, 'status': 'blocked' if missing else 'eligible_for_review',
            'missing_or_unconfirmed': missing,
            'scope': 'Evidence gate only; no statistical or visual approval.'}


def suggest(facts):
    validate_facts(facts)
    candidates = [chart for chart in REQUIREMENTS if not missing_facts(chart, facts)]
    return {'status': 'eligible_for_review' if candidates else 'no_match',
            'candidates': candidates,
            'scope': 'Candidates among the listed rules, based on supplied facts. Select by the research question.'}


def main():
    args = sys.argv[1:]
    usage = 'Usage: chart_guard.py --list | CHART FACTS.json | --suggest FACTS.json'
    if args in (['-h'], ['--help']):
        print(usage)
        return 0
    if args == ['--list']:
        print(json.dumps(REQUIREMENTS, indent=2))
        return 0
    if len(args) != 2:
        print(usage, file=sys.stderr)
        return 2
    try:
        mode, path = args
        with open(path, encoding='utf-8-sig') as f:
            facts = json.load(f)
        result = suggest(facts) if mode == '--suggest' else check(mode, facts)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['status'] == 'eligible_for_review' else 1
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
