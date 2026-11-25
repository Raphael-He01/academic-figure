import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
import zipfile


script = Path(__file__).resolve().parents[1] / 'scripts/package_release.py'
spec = importlib.util.spec_from_file_location('package_release', script)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class PackageReleaseTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='figure release ')
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.root = self.workspace / 'source'
        self.root.mkdir()
        for name in release.REQUIRED_FILES:
            self.add_fixture(name, 'public content\n')
        self.destination = self.workspace / 'new release.zip'

    def add_fixture(self, name, contents):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding='utf-8')

    def test_portable_members_and_repack(self):
        included = [
            '.github/workflows/checks.yml',
            'assets/r-template/.Rprofile',
            'assets/r-template/renv/activate.R',
            'references/示例.md',
        ]
        excluded = [
            'Rplots.pdf', '.Rhistory', 'scratch.txt', 'RELEASE_SHA256.json',
            'examples/Rplots.pdf', 'assets/r-template/renv/library/installed.R',
            'references/._resource', 'examples/artifacts/result.pdf',
        ]
        for name in included + excluded:
            self.add_fixture(name, name)
        result = release.package(self.root, self.destination)
        self.assertEqual(result['sha256'], hashlib.sha256(self.destination.read_bytes()).hexdigest())
        extracted = self.workspace / 'extracted'
        with zipfile.ZipFile(self.destination) as archive:
            names = archive.namelist()
            checksums = json.loads(archive.read(release.MANIFEST))
            self.assertEqual(set(checksums), set(included) | set(release.REQUIRED_FILES))
            self.assertEqual(len(names), len(set(names)))
            for name in included:
                self.assertIn(release.PREFIX + name, names)
            archive.extractall(extracted)
        second = self.workspace / 'repacked.zip'
        os.utime(extracted / 'academic-figure' / 'LICENSE', (1000000000, 1000000000))
        release.package(extracted / 'academic-figure', second)
        release.verify_archive(second, checksums)
        self.assertEqual(second.read_bytes(), self.destination.read_bytes())

    def test_each_third_party_notice_is_required_for_distribution(self):
        for name in ('THIRD_PARTY_NOTICES.md', 'LICENSES/ARS-NOTICE.txt',
                     'LICENSES/CC-BY-NC-4.0.txt', 'LICENSES/SOURCES.md'):
            with self.subTest(name=name):
                (self.root / name).unlink()
                with self.assertRaisesRegex(ValueError, 'Missing release files') as failure:
                    release.package(self.root, self.destination)
                self.assertIn(name, str(failure.exception))
                self.assertFalse(self.destination.exists())
                self.add_fixture(name, 'public content\n')

    def test_refuses_overwrite_internal_output_and_missing_core_files(self):
        self.destination.write_bytes(b'keep this')
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            release.package(self.root, self.destination)
        self.assertEqual(self.destination.read_bytes(), b'keep this')
        with self.assertRaisesRegex(ValueError, 'outside'):
            release.package(self.root, self.root / 'output.zip')
        (self.root / 'SKILL.md').unlink()
        with self.assertRaisesRegex(ValueError, 'SKILL.md'):
            release.package(self.root, self.workspace / 'incomplete.zip')
        self.assertFalse((self.workspace / 'incomplete.zip').exists())

    def test_refuses_symlink_and_keeps_destination_clean(self):
        path = self.workspace / 'outside.txt'
        path.write_text('not a release input', encoding='utf-8')
        (self.root / 'references').mkdir()
        try:
            (self.root / 'references/link.txt').symlink_to(path)
        except OSError:
            self.skipTest('creating a symlink is unavailable')
        with self.assertRaisesRegex(ValueError, 'Unexpected link'):
            release.package(self.root, self.destination)
        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.workspace.glob('.academic-figure-*')), [])
