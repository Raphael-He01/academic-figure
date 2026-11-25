"""A public release checkout contains everything needed to build both share packs."""
import base64
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.ids = set()
        self.downloads = {}

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for attribute in ("href", "src"):
            if attribute in attrs:
                self.urls.append(attrs[attribute])
        if "download" in attrs:
            self.downloads[attrs["download"]] = attrs["href"]


@unittest.skipUnless(importlib.util.find_spec("pymupdf"), "PyMuPDF builds the palette overview")
class Distribution(unittest.TestCase):
    def test_rebuild_from_clean_release_and_follow_offline_links(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            source = directory / "source.zip"
            subprocess.run([sys.executable, "-B", str(ROOT / "scripts/package_release.py"), str(source)],
                           check=True, capture_output=True)
            with ZipFile(source) as archive:
                archive.extractall(directory / "clone")
            clone = directory / "clone/academic-figure"
            output = directory / "release assets"
            subprocess.run([sys.executable, "-B", str(clone / "scripts/build_distribution.py"), str(output)],
                           check=True, capture_output=True)
            for line in (output / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
                digest, filename = line.split("  ", 1)
                self.assertEqual(digest, hashlib.sha256((output / filename).read_bytes()).hexdigest())
            with ZipFile(output / "Academic-Figure-Trial.zip") as trial:
                trial.extractall(directory / "trial")
            entry = next((directory / "trial").glob("*/START.html"))
            for name in ["START.html", "ROUTES.html"]:
                parser = PageLinks()
                parser.feed((entry.parent / name).read_text(encoding="utf-8"))
                if name == "START.html":
                    for fixture in ("mixed-script.pdf", "mixed-script.svg", "mixed-script.png",
                                    "mixed-script.json", "palette-swatches.png"):
                        self.assertIn("academic-figure/examples/mixed-script/" + fixture, parser.urls)
                    demo = entry.parent / "Statistical-Demo"
                    self.assertTrue((demo / "scripts/check_r_project.R").is_file())
                    profile = (demo / ".Rprofile").read_text(encoding="utf-8")
                    commands = [line for line in profile.splitlines() if line.strip() and not line.lstrip().startswith("#")]
                    self.assertEqual(commands, [], "Opening the trial must not bootstrap packages")
                for url in parser.urls:
                    link = urlsplit(url)
                    self.assertFalse(link.scheme, url)
                    if link.path:
                        target = (entry.parent / link.path).resolve()
                        self.assertTrue(target.is_relative_to(entry.parent.resolve()) and target.is_file(), url)
                    elif link.fragment:
                        self.assertIn(link.fragment, parser.ids)
            with ZipFile(output / "Academic-Figure-Palettes.zip") as archive:
                page = archive.read("index.html")
                self.assertEqual(page, (output / "site/index.html").read_bytes())
                self.assertIn("科研调色谱", page.decode("utf-8"))
                parser = PageLinks()
                parser.feed(page.decode("utf-8"))
                self.assertTrue(all(url.startswith(("#", "data:")) for url in parser.urls))
                encoded_json = parser.downloads["academic-figure-palettes.json"].split(",", 1)[1]
                self.assertEqual(json.loads(base64.b64decode(encoded_json)),
                                 json.loads((clone / "assets/palettes/catalog.json").read_text(encoding="utf-8")))
                encoded_png = parser.downloads["palettes.png"].split(",", 1)[1]
                self.assertEqual(base64.b64decode(encoded_png), archive.read("palettes.png"))
