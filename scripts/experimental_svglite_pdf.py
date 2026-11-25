#!/usr/bin/env python3
"""Experimental svglite SVG conversion; visual and scientific QA remain mandatory."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
SHAPES = {'line', 'rect', 'circle', 'path', 'polygon', 'polyline'}
FEATURES = {
    'clip-path': 'clipping', 'stroke-dasharray': 'dashed lines',
    'opacity': 'opacity', 'fill-opacity': 'opacity', 'stroke-opacity': 'opacity',
    'mask': 'masking', 'filter': 'filters',
}


def declarations(style):
    result = {}
    for entry in style.split(';'):
        if not entry.strip():
            continue
        name, sep, value = entry.partition(':')
        if not sep or not name.strip() or not value.strip() or '!important' in value.lower():
            raise ValueError('unexpected CSS declaration in svglite styles')
        result[name.strip().lower()] = value.strip()
    return result


def stylesheet_defaults(root):
    defaults = {}
    css_features = set()
    for node in root.iter(f'{{{SVG}}}style'):
        css = re.sub(r'/\*.*?\*/', '', node.text or '', flags=re.S).strip()
        while css:
            block = re.match(r'([^{}]+)\{([^{}]*)\}', css)
            if not block:
                raise ValueError('unexpected svglite stylesheet syntax')
            props = declarations(block[2])
            css_features.update(FEATURES[k] for k in props if k in FEATURES)
            for part in block[1].split(','):
                selector = ' '.join(part.split())
                if selector == '.svglite text' and props == {'white-space': 'pre'}:
                    continue
                if selector == '.svglite g.glyphgroup path' and props == {'fill': 'inherit', 'stroke': 'none'}:
                    continue
                match = re.fullmatch(r'\.svglite (\w+)', selector)
                if not match or match[1] not in SHAPES:
                    raise ValueError('unexpected svglite stylesheet selector: ' + selector)
                defaults.setdefault(match[1], {}).update(props)
            css = css[block.end():].strip()
    if not any(props.get('fill', '').lower() == 'none' for props in defaults.values()):
        raise ValueError('expected svglite fill:none default not found')
    return defaults, css_features


def prepare_svg(source):
    root = ET.fromstring(source)
    if root.tag != f'{{{SVG}}}svg' or not any('svglite' in n.get('class', '').split() for n in root.iter()):
        raise ValueError('expected an SVG with an svglite class')
    defaults, features = stylesheet_defaults(root)
    count = 0

    def visit(node, in_scope=False, glyph=False, clipping_shape=False):
        nonlocal count
        classes = node.get('class', '').split()
        tag = node.tag.removeprefix(f'{{{SVG}}}')
        style = declarations(node.get('style', ''))
        features.update(FEATURES[k] for k in node.attrib.keys() | style.keys() if k in FEATURES)
        if glyph and tag == 'path':
            # The renderer can turn inherited glyph fills black.
            features.add('inherited glyph paint')
        elif in_scope and tag in defaults and not clipping_shape:
            # Inline CSS wins over selector rules, which win over presentation
            # attributes. MuPDF takes the first duplicated property, so emit it once.
            merged = {**defaults[tag], **style}
            count += int(merged.get('fill', '').lower() == 'none' and 'fill' not in style)
            for key in merged:
                node.attrib.pop(key, None)
            node.set('style', '; '.join(f'{k}: {v}' for k, v in merged.items()))
        for child in node:
            visit(child, in_scope or 'svglite' in classes,
                  glyph or (tag == 'g' and 'glyphgroup' in classes),
                  clipping_shape or tag == 'clipPath')

    visit(root)
    return ET.tostring(root, encoding='utf-8'), count, sorted(features)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('svg', type=Path)
    p.add_argument('pdf', type=Path)
    p.add_argument('--allow-unsupported', action='store_true', help='experimental inspection only; output still requires manual review')
    args = p.parse_args()
    try:
        import pymupdf
        source = args.svg.read_bytes()
        svg, count, unsupported = prepare_svg(source)
        if unsupported and not args.allow_unsupported:
            raise ValueError('unsupported visual features: ' + ', '.join(unsupported) + '; use --allow-unsupported only for inspection')
        if args.pdf.exists() or args.pdf.is_symlink():
            raise ValueError('output exists; refusing to overwrite')
        doc = pymupdf.open(stream=svg, filetype='svg')
        try:
            output = doc.convert_to_pdf()
        finally:
            doc.close()
        with args.pdf.open('xb') as f:
            f.write(output)
        print(json.dumps({'source_sha256': hashlib.sha256(source).hexdigest(),
                          'pdf_sha256': hashlib.sha256(output).hexdigest(),
                          'inlined_fill_defaults': count, 'acceptance': 'pending',
                          'unsupported_features': unsupported,
                          'scope': 'Experimental: inspect actual text, colour, clipping, transparency and layout.'}))
        return 0
    except (OSError, ET.ParseError, ValueError, UnicodeError, ImportError, RuntimeError) as e:
        print(f'conversion failed: {e}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
