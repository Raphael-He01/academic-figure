import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('profile_csv', ROOT / 'scripts/profile_csv.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ProfileCsvTest(unittest.TestCase):
    def test_keys_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'data.csv'
            p.write_text('id,value\na,1\na,NaN\n,\n', encoding='utf-8')
            before = p.read_bytes()
            result = module.profile(p, ['id'])
            self.assertEqual(result['rows'], 3)
            self.assertEqual(result['duplicate_complete_key_rows'], 1)
            self.assertEqual(result['incomplete_key_rows'], 1)
            self.assertEqual(result['columns'][1]['nonfinite_numeric'], 1)
            self.assertEqual(result['columns'][1]['meaning'], 'unconfirmed')
            self.assertEqual(p.read_bytes(), before)

    def test_bad_inputs_and_multiline(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'data.csv'
            for data in ('x,x\n1,2\n', 'x,y\n1\n'):
                p.write_text(data, encoding='utf-8')
                with self.assertRaises(ValueError):
                    module.profile(p)
            p.write_text('id,note\n1,"two\nlines"\n', encoding='utf-8')
            self.assertEqual(module.profile(p)['rows'], 1)
            with self.assertRaises(ValueError):
                module.profile(p, ['absent'])


if __name__ == '__main__':
    unittest.main()
