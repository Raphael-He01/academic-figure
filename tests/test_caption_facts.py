import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/caption_facts.py'


class CaptionFactsTest(unittest.TestCase):
    def test_refresh_detection_and_missing_fact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            template, facts, caption = [root / p for p in ('template', 'facts.json', 'caption')]
            template.write_text('n = ${n}; mean = ${mean}.', encoding='utf-8')
            facts.write_text('{"n":"12","mean":"2.5"}', encoding='utf-8')
            cmd = [sys.executable, str(SCRIPT)]
            self.assertEqual(subprocess.run(cmd + ['render', str(template), str(facts), str(caption)], capture_output=True).returncode, 0)
            facts.write_text('{"n":"13","mean":"2.5"}', encoding='utf-8')
            self.assertEqual(subprocess.run(cmd + ['verify', str(template), str(facts), str(caption)], capture_output=True).returncode, 1)
            facts.write_text('{"n":"13"}', encoding='utf-8')
            self.assertEqual(subprocess.run(cmd + ['verify', str(template), str(facts), str(caption)], capture_output=True).returncode, 2)
