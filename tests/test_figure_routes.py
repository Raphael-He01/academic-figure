"""Exercise the public figure-family lookup independently of the working directory."""
import re
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/figure_routes.py'


def lookup(*terms):
    with tempfile.TemporaryDirectory() as external:
        return subprocess.run([sys.executable, '-B', str(SCRIPT), *terms], cwd=external,
                              text=True, capture_output=True)


class FigureRouteTest(unittest.TestCase):
    def test_optional_check_keeps_keyword_matches_separate_from_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'confirmed facts.json'
            facts = dict(ordered_stages_confirmed=True, flow_unit_confirmed=True,
                         stage_totals_reconciled=True)
            path.write_text(json.dumps(facts), encoding='utf-8-sig')
            match = lookup('阶段', '--facts', str(path))
            self.assertEqual(match.returncode, 0, match.stderr)
            self.assertIn('stage_flow 缺少已确认条件：transition_links_verified', match.stdout)
            facts['transition_links_verified'] = True
            path.write_text(json.dumps(facts), encoding='utf-8')
            match = lookup('V08', '--facts', str(path))
            self.assertEqual(match.returncode, 0, match.stderr)
            self.assertIn('stage_flow 的显式条件已满足', match.stdout)
            manual = lookup('V25', '--facts', str(path))
            self.assertIn('人工核对', manual.stdout)
            self.assertNotIn('已满足', manual.stdout)
            for invalid in ('{"transition_links_verified": 1}', 'null', '{'):
                path.write_text(invalid, encoding='utf-8')
                self.assertEqual(lookup('V08', '--facts', str(path)).returncode, 2)

    def test_each_family_id_selects_one_usable_route(self):
        for i in range(1, 33):
            key = f'V{i:02d}'
            with self.subTest(key=key):
                result = lookup(key)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(re.findall(r'^V\d+\b', result.stdout, re.MULTILINE), [key])
                lines = result.stdout.splitlines()
                self.assertEqual(len(lines), 3)
                self.assertTrue(all(line.strip() for line in lines))

    def test_queries_match_question_and_encoding(self):
        for terms, key in [(('状态场', '粒子'), 'V04'), (('MEDOID', '图谱'), 'V06'),
                           (('v12', '三元'), 'V12')]:
            with self.subTest(terms=terms):
                result = lookup(*terms)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(re.findall(r'^V\d+\b', result.stdout, re.MULTILINE), [key])

    def test_no_matching_route_or_missing_query(self):
        for terms, code in [(('V33',), 1), (('V04', 'medoid'), 1), ((' ',), 2), ((), 2)]:
            with self.subTest(terms=terms):
                result = lookup(*terms)
                self.assertEqual(result.returncode, code)
                self.assertNotRegex(result.stdout, r'(?m)^V\d+\b')
