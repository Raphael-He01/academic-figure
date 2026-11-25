import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/print_svg_pdf.py'
FIGURE = '''<svg xmlns="http://www.w3.org/2000/svg" width="160pt" height="100pt"
viewBox="0 0 160 100" class="svglite">
<defs><clipPath id="clip"><rect x="10" y="10" width="40" height="20"/></clipPath></defs>
<rect width="160" height="100" fill="white"/>
<rect x="10" y="10" width="70" height="20" fill="red" opacity=".5" clip-path="url(#clip)"/>
<line x1="10" x2="140" y1="55" y2="55" stroke="black" stroke-width="4" stroke-dasharray="10 10"/>
<text x="10" y="85" font-size="10">Vector sample</text>
</svg>'''


def command(source, output, browser, *options):
    return subprocess.run(
        [sys.executable, '-B', str(SCRIPT), str(source), str(output), '--browser', browser, *options],
        capture_output=True, text=True, encoding='utf-8', timeout=70,
    )


class BrowserPDFTest(unittest.TestCase):
    def setUp(self):
        if importlib.util.find_spec('pymupdf') is None:
            self.skipTest('PyMuPDF unavailable')
        temp = tempfile.TemporaryDirectory(prefix='figure print ')
        self.addCleanup(temp.cleanup)
        self.source = Path(temp.name) / 'input.svg'
        self.output = Path(temp.name) / 'output.pdf'

    def test_rejects_external_image_before_printing(self):
        self.source.write_text(FIGURE.replace('</svg>', '<image href="outside.png"/></svg>'), encoding='utf-8')
        result = command(self.source, self.output, sys.executable)
        self.assertEqual(result.returncode, 2)
        self.assertIn('embedded PNG and JPEG', result.stderr)
        self.assertFalse(self.output.exists())

    def test_clipping_opacity_dashes_and_text(self):
        browser = os.environ.get('ACADEMIC_FIGURE_CHROMIUM')
        if not browser:
            self.skipTest('set ACADEMIC_FIGURE_CHROMIUM to a local executable')
        import pymupdf

        self.source.write_text(FIGURE, encoding='utf-8')
        result = command(self.source, self.output, browser, '--label', 'Vector sample')
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.assertEqual(record['image_resources'], 0)
        self.assertEqual(record['acceptance'], 'pending')
        self.assertGreater(record['vector_paths'], 0)
        with pymupdf.open(self.output) as document:
            pix = document[0].get_pixmap(matrix=pymupdf.Matrix(2, 2))
        red, green, blue = pix.pixel(40, 40)
        self.assertEqual(red, 255)
        self.assertTrue(120 < green < 140 and 120 < blue < 140)
        self.assertEqual(pix.pixel(140, 40), (255, 255, 255))
        self.assertEqual(pix.pixel(30, 110), (0, 0, 0))
        self.assertEqual(pix.pixel(50, 110), (255, 255, 255))
        before = self.output.read_bytes()
        result = command(self.source, self.output, browser)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.output.read_bytes(), before)
