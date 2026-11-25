import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('chart_guard', Path(__file__).resolve().parents[1] / 'scripts/chart_guard.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class ChartGuardTest(unittest.TestCase):
    def test_boundaries(self):
        cases = [
            ('paired_lines', {'paired_ids_confirmed': True}, 'blocked'),
            ('paired_lines', {'paired_ids_confirmed': True, 'paired_observations_available': True}, 'eligible_for_review'),
            ('violin', {'individual_values_available': False}, 'blocked'),
            ('error_bars', {'interval_values_available': True}, 'blocked'),
            ('survival_curve', {'event_times_available': True}, 'blocked'),
        ]
        for chart, facts, expected in cases:
            with self.subTest(chart=chart, facts=facts):
                self.assertEqual(guard.check(chart, facts)['status'], expected)

    def test_unknowns_do_not_pass(self):
        with self.assertRaises(ValueError):
            guard.check('violin', {'individual_values_available': 'true'})
        with self.assertRaises(ValueError):
            guard.check('unknown', {})

    def test_model_outputs_require_evidence_for_the_relationship(self):
        cases = {
            'posterior_pairs': {
                'joint_draw_keys_verified', 'two_or_more_parameters_available',
                'posterior_sampling_confirmed', 'draw_weights_accounted_for',
            },
            'stage_flow': {
                'ordered_stages_confirmed', 'transition_links_verified',
                'flow_unit_confirmed', 'stage_totals_reconciled',
            },
            'contribution_waterfall': {
                'additive_definition_confirmed', 'common_additive_scale_confirmed',
                'baseline_and_total_available', 'contributions_reconciled',
            },
            'weighted_state_field': {
                'state_samples_available', 'time_schedule_confirmed',
                'within_time_weights_verified', 'common_state_bin_edges_confirmed',
            },
            'sample_feature_atlas': {
                'sample_feature_values_available', 'sample_ids_verified',
                'annotation_join_verified', 'feature_scale_confirmed',
            },
        }
        for chart, keys in cases.items():
            confirmed = dict.fromkeys(keys, True)
            with self.subTest(chart=chart):
                self.assertEqual(guard.suggest(confirmed)['candidates'], [chart])
            for key in keys:
                partial = confirmed.copy()
                del partial[key]
                with self.subTest(chart=chart, missing=key):
                    self.assertEqual(guard.check(chart, partial)['missing_or_unconfirmed'], [key])
                    partial[key] = False
                    self.assertEqual(guard.suggest(partial)['status'], 'no_match')

    def test_multiple_supported_questions_stay_open(self):
        facts = {'individual_values_available': True, 'paired_ids_confirmed': True,
                 'paired_observations_available': True}
        self.assertCountEqual(guard.suggest(facts)['candidates'], ['paired_lines', 'violin'])
        self.assertEqual(guard.suggest({})['candidates'], [])

    def test_equal_stage_totals_hide_real_transitions(self):
        example = Path(guard.__file__).resolve().parents[1] / 'examples/stage-flow/compare.py'
        run = subprocess.run([sys.executable, '-B', str(example)], capture_output=True,
                             text=True, check=True)
        result = json.loads(run.stdout)
        self.assertEqual(list(result['stage_counts'].values()), [{'A': 3, 'B': 3}] * 3)
        self.assertEqual(result['items_changing_desk'], [4, 4])
        self.assertEqual(result['with_item_paths'], ['stage_flow'])
        self.assertEqual(result['with_stage_counts_only']['status'], 'blocked')

    def test_model_selection_cli(self):
        script = Path(guard.__file__)
        def run(*args):
            return subprocess.run([sys.executable, str(script), *args],
                                  capture_output=True, text=True, check=False)
        catalog = run('--list')
        self.assertEqual(catalog.returncode, 0, catalog.stderr)
        catalog = json.loads(catalog.stdout)
        with tempfile.TemporaryDirectory() as directory:
            facts = Path(directory) / 'checked facts.json'
            supplied = dict.fromkeys(catalog['stage_flow'], True)
            facts.write_text(json.dumps(supplied), encoding='utf-8-sig')
            result = run('--suggest', facts)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['candidates'], ['stage_flow'])
            supplied.pop('transition_links_verified')
            facts.write_text(json.dumps(supplied), encoding='utf-8')
            self.assertEqual(run('--suggest', facts).returncode, 1)
            result = run('stage_flow', facts)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['missing_or_unconfirmed'], ['transition_links_verified'])
            facts.write_text('{"ordered_stages_confirmed": "true"}', encoding='utf-8')
            self.assertEqual(run('--suggest', facts).returncode, 2)

    def test_state_and_atlas_cli_with_missing_and_verified_relationships(self):
        script = Path(guard.__file__)
        catalog = json.loads(subprocess.check_output([sys.executable, str(script), '--list'], text=True))
        routes = {'weighted_state_field': 'within_time_weights_verified',
                  'sample_feature_atlas': 'annotation_join_verified'}
        self.assertTrue(routes.keys() <= catalog.keys())
        with tempfile.TemporaryDirectory() as directory:
            facts = Path(directory) / 'model facts.json'
            both = {key: True for chart in routes for key in catalog[chart]}
            facts.write_text(json.dumps(both), encoding='utf-8')
            result = subprocess.check_output([sys.executable, str(script), '--suggest', str(facts)], text=True)
            self.assertCountEqual(json.loads(result)['candidates'], routes)
            for chart, missing in routes.items():
                facts.write_text(json.dumps(dict(both, **{missing: False})), encoding='utf-8')
                result = subprocess.run([sys.executable, str(script), chart, str(facts)],
                                        text=True, capture_output=True)
                with self.subTest(chart=chart):
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(json.loads(result.stdout)['missing_or_unconfirmed'], [missing])
