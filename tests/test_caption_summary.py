import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/check_caption_summary.py'


class SummaryCheck(unittest.TestCase):
    def test_match_mismatch_and_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); data = root/'data.csv'; facts = root/'facts.json'
            data.write_text('value\n1\n2\n3\n'); facts.write_text(json.dumps({'n': 3, 'mean': '2.0', 'decimals': 1}))
            cmd = [sys.executable, str(SCRIPT), str(data), 'value', str(facts)]
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            facts.write_text(json.dumps({'n': 3, 'mean': '2.1', 'decimals': 1}))
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 1)
            data.write_text('value\n1\nNA\n')
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)
