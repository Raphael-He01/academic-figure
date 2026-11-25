#!/usr/bin/env python3
"""Create a clean review archive from this repository; never upload or overwrite."""
import argparse
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
import unicodedata
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = {
    '.gitattributes', '.gitignore', 'CHANGELOG.md', 'CITATION.cff', 'LICENSE',
    'README.md', 'SKILL.md', 'THIRD_PARTY_NOTICES.md', 'VALIDATION.md', 'VERSION',
    'academic-figure.Rproj', 'requirements-qa.txt',
}
PUBLIC_DIRS = {'.github', 'LICENSES', 'agents', 'assets', 'examples', 'references', 'scripts', 'tests'}
REQUIRED_FILES = {
    'LICENSE', 'README.md', 'SKILL.md', 'VERSION', 'THIRD_PARTY_NOTICES.md',
    'LICENSES/ARS-NOTICE.txt', 'LICENSES/CC-BY-NC-4.0.txt', 'LICENSES/SOURCES.md',
}
EXCLUDED = {
    '.DS_Store', '.git', '.Rproj.user', '.Rhistory', '.RData', '.Ruserdata',
    'Rplots.pdf', 'RELEASE_SHA256.json', '__pycache__', '.pytest_cache', '.venv',
    'artifacts', 'private', 'node_modules', 'tmp',
}
RENV_CACHE = {'library', 'staging', 'python', 'sandbox', 'cache', 'source', 'cellar'}
PREFIX = 'academic-figure/'
MANIFEST = PREFIX + 'RELEASE_SHA256.json'


def source_files(root):
    def visit(directory):
        seen = set()
        for path in sorted(directory.iterdir(), key=lambda path: path.name):
            name = path.name
            if directory == root and name not in PUBLIC_DIRS and name not in PUBLIC_FILES:
                continue
            if name in EXCLUDED or name.startswith(('.env', '._')) or path.suffix.lower() in {'.pyc', '.pyo', '.opju'}:
                continue
            if directory.name == 'renv' and name in RENV_CACHE:
                continue
            relative = path.relative_to(root)
            if path.is_symlink() or re.search(r'icm[-_ ]?\d{6,}', name, re.I):
                raise ValueError(f'Unexpected link or private source in release inputs: {relative}')
            if (any(c in '<>:"/\\|?*' or ord(c) < 32 for c in name) or name.endswith(('.', ' '))
                    or re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(\..*)?', name, re.I)):
                raise ValueError(f'Filename cannot be extracted portably: {relative}')
            key = unicodedata.normalize('NFC', name).casefold()
            if key in seen:
                raise ValueError(f'Filenames collide on a case-insensitive filesystem: {relative}')
            seen.add(key)
            mode = path.stat().st_mode
            if directory == root and (name in PUBLIC_DIRS) != stat.S_ISDIR(mode):
                raise ValueError(f'Unexpected type for release input: {relative}')
            if stat.S_ISDIR(mode):
                yield from visit(path)
            elif stat.S_ISREG(mode):
                yield path
            else:
                raise ValueError(f'Unexpected special file in release inputs: {relative}')
    return visit(root)


def verify_archive(path, checksums):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        expected = {PREFIX + name for name in checksums} | {MANIFEST}
        if len(names) != len(expected) or set(names) != expected:
            raise ValueError('Release archive contains missing, extra or duplicate entries')
        stored = json.loads(archive.read(MANIFEST))
        if stored != checksums:
            raise ValueError('Release manifest does not match the packaged inputs')
        for name, digest in stored.items():
            if hashlib.sha256(archive.read(PREFIX + name)).hexdigest() != digest:
                raise ValueError(f'Archived bytes failed verification: {name}')


def write_member(archive, name, data):
    # The ZIP epoch and regular-file mode also survive extraction and repacking.
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)


def publish(staged, destination):
    # A hard link publishes the verified file in one operation without overwriting.
    try:
        os.link(staged, destination)
        return
    except OSError as error:
        if error.errno not in {errno.ENOSYS, errno.EOPNOTSUPP, errno.EPERM, errno.EACCES, errno.EXDEV}:
            raise
    # Removable or shared filesystems may not support hard links.
    with staged.open('rb') as source:
        output = destination.open('xb')
        try:
            with output:
                shutil.copyfileobj(source, output)
        except BaseException:
            destination.unlink()
            raise


def package(root, destination):
    root = root.resolve()
    destination = destination.parent.resolve() / destination.name
    if destination.exists() or destination.is_symlink():
        raise ValueError('Destination exists; refusing overwrite')
    if destination.is_relative_to(root):
        raise ValueError('Keep the archive outside the source tree')
    missing = sorted(name for name in REQUIRED_FILES if not (root / name).is_file())
    if missing:
        raise ValueError('Missing release files: ' + ', '.join(missing))
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.academic-figure-', dir=destination.parent) as staging:
        staged = Path(staging) / 'release.zip'
        hashes = {}
        with zipfile.ZipFile(staged, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for path in source_files(root):
                relative = path.relative_to(root).as_posix()
                data = path.read_bytes()
                write_member(archive, PREFIX + relative, data)
                hashes[relative] = hashlib.sha256(data).hexdigest()
            write_member(archive, MANIFEST, json.dumps(hashes, ensure_ascii=False, indent=2))
        verify_archive(staged, hashes)
        digest = hashlib.sha256(staged.read_bytes()).hexdigest()
        publish(staged, destination)
    return {'archive': str(destination), 'files': len(hashes), 'sha256': digest, 'archive_check': 'pass'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(package(ROOT, args.destination), ensure_ascii=False))
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        parser.exit(2, f'Packaging failed: {error}\n')


if __name__ == '__main__':
    main()
