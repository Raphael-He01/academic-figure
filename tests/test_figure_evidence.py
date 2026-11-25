import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/figure_evidence.py'


class EvidenceTest(unittest.TestCase):
    def test_changed_caption_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('data.csv', 'figure.svg', 'caption.md'):
                (root / name).write_text(name)
            record = root / 'record.json'
            cmd = [sys.executable, str(SCRIPT), 'create', str(record), '--data', str(root/'data.csv'),
                   '--figure', str(root/'figure.svg'), '--caption', str(root/'caption.md')]
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)
            check = [sys.executable, str(SCRIPT), 'verify', str(record)]
            self.assertEqual(subprocess.run(check, capture_output=True).returncode, 0)
            (root/'caption.md').write_text('changed')
            result = subprocess.run(check, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['changed'], ['caption'])
