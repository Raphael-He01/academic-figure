import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/experimental_svglite_pdf.py'


@unittest.skipUnless(importlib.util.find_spec('pymupdf'), 'PyMuPDF unavailable')
class ExperimentalSvgTest(unittest.TestCase):
    def test_legend_is_not_obscured_and_refuse_overwrite(self):
        import pymupdf
        svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
        <g class="svglite"><style>.svglite line, .svglite rect { fill: none; stroke: #000000; }</style>
        <rect x="10" y="10" width="80" height="80" style="fill: #ff0000; stroke: none;"/>
        <rect x="10" y="10" width="80" height="80" style="stroke: #000000;"/></g></svg>'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp); src = path/'source.svg'; dst = path/'figure.pdf'
            src.write_text(svg)
            cmd = [sys.executable, str(SCRIPT), str(src), str(dst)]
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            with pymupdf.open(dst) as doc:
                pix = doc[0].get_pixmap()
                self.assertEqual(tuple(pix.pixel(50, 50)[:3]), (255, 0, 0))
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)
            src.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            self.assertEqual(subprocess.run([sys.executable, str(SCRIPT), str(src), str(path/'bad.pdf')], capture_output=True).returncode, 2)

    def test_fill_and_stroke_follow_selector_scope_in_rendered_pdf(self):
        import pymupdf
        svg = """<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80">
        <desc>Style notes: opacity: full</desc>
        <g class="figure svglite"><style>
        .svglite line, .svglite rect {fill:none; stroke: #000000;}
        </style>
        <rect width="120" height="80" style="fill: #ff0000; stroke: none"/>
        <rect x="5" y="5" width="110" height="70"/>
        <line x1="10" y1="10" x2="90" y2="10" style="stroke-width: 4"/>
        <circle cx="25" cy="30" r="6" style="stroke: none"/>
        <rect x="45" y="25" width="10" height="10" fill="#00ff00"/>
        <rect x="70" y="25" width="10" height="10" fill="#ff0000" style="fill:#00ff00"/>
        </g><circle cx="100" cy="30" r="6" style="stroke:none"/></svg>"""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / 'sample.svg'
            dst = Path(tmp) / 'figure.pdf'
            src.write_text(svg)
            run = subprocess.run([sys.executable, str(SCRIPT), str(src), str(dst)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)['unsupported_features'], [])
            with pymupdf.open(dst) as doc:
                pix = doc[0].get_pixmap()
                # Inspect the composited pixels, including a mark outside the svglite group.
                for point, color in {
                    (60, 50): (255, 0, 0), (40, 10): (0, 0, 0),
                    (25, 30): (0, 0, 0), (50, 30): (255, 0, 0),
                    (75, 30): (0, 255, 0), (100, 30): (0, 0, 0)
                }.items():
                    with self.subTest(point=point):
                        self.assertEqual(tuple(pix.pixel(*point)[:3]), color)

    def test_unrelated_rule_cannot_supply_svglite_default(self):
        svg = """<svg xmlns="http://www.w3.org/2000/svg"><g class="svglite">
        <style>.svglite line {stroke:#000;} .elsewhere {fill:none;}</style>
        <rect width="20" height="20" style="stroke:red"/></g></svg>"""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / 'source.svg'
            dst = Path(tmp) / 'out.pdf'
            src.write_text(svg)
            result = subprocess.run([sys.executable, str(SCRIPT), str(src), str(dst)], capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(dst.exists())

    def test_unsupported_features_block_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for feature in ('clip-path="url(#clip)"', 'style="stroke-dasharray: 2,2"', 'style="fill-opacity: 0.2"',
                            'style="OPACITY: 0.2"', 'mask="url(#left)"', 'filter="url(#blur)"'):
                src = root / 'test.svg'; dst = root / 'out.pdf'
                src.write_text('<svg xmlns="http://www.w3.org/2000/svg"><g class="svglite"><style>.svglite line { fill: none; }</style><rect ' + feature + '/></g></svg>')
                result = subprocess.run([sys.executable, str(SCRIPT), str(src), str(dst)], capture_output=True)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(dst.exists())
