#!/usr/bin/env python3
"""Print a self-contained svglite figure to a draft PDF using a local Chromium browser."""

import argparse
from base64 import b64encode
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from qa.audit_pdf_fonts import inspect_pdf


SVG = '{http://www.w3.org/2000/svg}'
XLINK = '{http://www.w3.org/1999/xlink}'
STATIC_TAGS = {
    'svg', 'defs', 'clipPath', 'g', 'style', 'circle', 'ellipse', 'line', 'path',
    'polygon', 'polyline', 'rect', 'text', 'tspan', 'linearGradient',
    'radialGradient', 'stop', 'image', 'title', 'desc',
}
ET.register_namespace('', SVG[1:-1])
ET.register_namespace('xlink', XLINK[1:-1])


def parse_figure(source):
    root = ET.fromstring(source)
    if root.tag != SVG + 'svg' or not any('svglite' in n.get('class', '').split() for n in root.iter()):
        raise ValueError('expected a svglite SVG document')
    sizes = []
    for key in ('width', 'height'):
        match = re.fullmatch(r'(\d+(?:\.\d+)?)pt', root.get(key, ''), re.ASCII)
        if not match or not math.isfinite(float(match[1])) or float(match[1]) <= 0:
            raise ValueError(f'expected an explicit positive {key} in points')
        sizes.append(float(match[1]))
    for node in root.iter():
        tag = node.tag.removeprefix(SVG)
        if node.tag != SVG + tag or tag not in STATIC_TAGS:
            raise ValueError(f'unsupported element: {node.tag}')
        for attr, value in node.attrib.items():
            if attr in ('href', XLINK + 'href'):
                if tag != 'image' or not re.fullmatch(r'data:image/(?:png|jpeg);base64,[A-Za-z0-9+/=\s]+', value):
                    raise ValueError('only embedded PNG and JPEG images are supported')
        # svglite references local clipping paths and gradients by fragment ID.
        css = ' '.join([*node.attrib.values(), node.text or ''] if tag == 'style' else node.attrib.values())
        if re.search(r'@import\b', css, re.I) or any(
            not url.strip().strip("'\x22").startswith('#')
            for url in re.findall(r'url\(([^)]*)\)', css, re.I)
        ):
            raise ValueError('external resources are not supported')
    return root, tuple(sizes)


def embed_label_font(root, labels, path):
    from fontTools import subset
    from fontTools.ttLib import TTFont, TTLibError

    if path.suffix.lower() not in ('.ttf', '.otf'):
        raise ValueError('select a single TTF or OTF font')
    nodes = [n for n in root.iter(SVG + 'text') if n.text in labels and not len(n)]
    if {n.text for n in nodes} != set(labels):
        raise ValueError('each requested label must match the exact text of an SVG text element')
    data = path.read_bytes()
    characters = set(''.join(labels))
    try:
        with TTFont(io.BytesIO(data)) as font:
            # Respect restricted embeddings, disallowed subsetting and bitmap-only permissions.
            if 'OS/2' not in font or font['OS/2'].fsType & 0x302:
                raise ValueError('font flags do not allow an outline subset')
            missing = characters.difference(chr(c) for c in (font.getBestCmap() or {}))
            if missing:
                raise ValueError('font lacks glyphs for ' + ', '.join(f'U+{ord(c):04X}' for c in sorted(missing)))
            options = subset.Options()
            options.recalc_timestamp = False
            sub = subset.Subsetter(options=options)
            sub.populate(unicodes=map(ord, characters))
            sub.subset(font)
            buffer = io.BytesIO()
            font.save(buffer)
    except TTLibError as exc:
        raise ValueError(f'cannot subset the supplied font: {exc}') from exc
    font_data = b64encode(buffer.getvalue()).decode('ascii')
    media_type = 'font/ttf' if path.suffix.lower() == '.ttf' else 'font/otf'
    definition = ET.Element(SVG + 'style')
    definition.text = f'@font-face {{font-family: FigureLabelSubset; src: url(data:{media_type};base64,{font_data});}}'
    root.insert(0, definition)
    for node in nodes:
        old_style = node.get('style', '')
        node.set('style', old_style + '; font-family: FigureLabelSubset;')
    return hashlib.sha256(data).hexdigest()


def print_pdf(args):
    import pymupdf

    if args.pdf.exists() or args.pdf.is_symlink():
        raise ValueError('output exists')
    if not args.browser.is_file():
        raise ValueError('provide the path to a local Chromium browser executable')
    if args.font and not args.label:
        raise ValueError('--font requires at least one --label')
    source = args.svg.read_bytes()
    root, (width, height) = parse_figure(source)
    font_hash = embed_label_font(root, args.label, args.font) if args.font else None
    svg = ET.tostring(root, encoding='unicode')
    with tempfile.TemporaryDirectory(prefix='figure-print-') as folder:
        work = Path(folder)
        draft, html = work / 'figure.pdf', work / 'figure.html'
        html.write_text(
            '<!doctype html><meta charset="utf-8"><title>Figure</title>'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
            "style-src 'unsafe-inline'; font-src data:; img-src data:\">"
            '<style>'
            f'@page {{ size: {width:g}pt {height:g}pt; margin: 0; }}'
            'html, body { margin: 0; padding: 0; } svg { display: block; }'
            '</style>' + svg,
            encoding='utf-8',
        )
        run = subprocess.run([
            str(args.browser.resolve()), '--headless', '--disable-extensions',
            '--disable-background-networking', '--disable-component-update',
            '--no-first-run', '--no-default-browser-check',
            f'--user-data-dir={work / "profile"}', '--no-pdf-header-footer',
            f'--print-to-pdf={draft}', html.as_uri(),
        ], capture_output=True, timeout=60)
        if run.returncode or not draft.is_file():
            raise ValueError(f'Chromium PDF export failed (exit {run.returncode})')
        font_report = {'pages': [], 'fonts': []}
        if inspect_pdf(draft, pymupdf, font_report):
            raise ValueError('PDF did not pass font embedding checks: ' + font_report['message'])
        with pymupdf.open(draft) as document:
            if len(document) != 1:
                raise ValueError(f'expected a single PDF page, got {len(document)}')
            page = document[0]
            actual = (page.rect.width, page.rect.height)
            if any(abs(expected - measured) > 1 for expected, measured in zip((width, height), actual)):
                raise ValueError('PDF page differs from the source by more than one point')
            text = page.get_text()
            if any(label not in text for label in args.label):
                raise ValueError('an expected label did not survive exact PDF text extraction')
            metadata = {
                'renderer': document.metadata.get('producer'), 'expected_pt': [width, height],
                'actual_pt': list(actual), 'label_count': len(args.label),
                'font_embedding': font_report['status'],
                'vector_paths': len(page.get_drawings()), 'image_resources': len(page.get_images()),
            }
            if not metadata['vector_paths']:
                raise ValueError('no vector drawing paths found in the printed PDF')
        pdf = draft.read_bytes()
    with args.pdf.open('xb') as handle:
        handle.write(pdf)
    return {
        **metadata, 'acceptance': 'pending',
        'source_sha256': hashlib.sha256(source).hexdigest(),
        'pdf_sha256': hashlib.sha256(pdf).hexdigest(), 'label_font_sha256': font_hash,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('svg', type=Path)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--browser', type=Path, required=True, help='local Chromium executable')
    parser.add_argument('--label', action='append', default=[], help='require exact PDF text for this SVG label')
    parser.add_argument('--font', type=Path, help='local embeddable TTF or OTF for the specified labels')
    args = parser.parse_args()
    try:
        print(json.dumps(print_pdf(args), ensure_ascii=False))
    except (OSError, ImportError, ET.ParseError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        parser.exit(2, f'PDF draft failed: {exc}\n')


if __name__ == '__main__':
    main()
