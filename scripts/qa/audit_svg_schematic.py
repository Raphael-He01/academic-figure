#!/usr/bin/env python3
# Adapted from nature-figure (Apache-2.0). QA-only helper; it never renders a figure.
# Modified: fixed rotation math, checked full-document DTD declarations and finite thresholds, and rejected unsupported transforms/styles as not auditable.
"""Audit a hand-built SVG schematic against final-size journal rules.

Checks, using only the standard library:

* effective text size at final physical size (font-size, ``scale``/``matrix``
  transforms, and the ``viewBox`` to ``width`` scale) against a floor and ceiling;
* canvas width against a journal maximum;
* text anchored outside the canvas;
* constructs that do not survive production: scripts, ``foreignObject``,
  gradients, filters, and external references.

It does not detect overlaps between boxes, crossing arrows, or outlined text.
Transform scale is area-equivalent, so anisotropic glyph compression requires
visual inspection. CSS stylesheets, reused elements and unsupported transforms
are reported as not auditable. It never replaces final-size visual inspection.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from xml.etree import ElementTree as ET  # nosec B405 - DTDs and entities are rejected before parsing

PT_PER_UNIT = {"pt": 1.0, "px": 0.75, "mm": 72 / 25.4, "cm": 72 / 2.54, "in": 72.0, "": None}
NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?"
LENGTH = re.compile(rf"^\s*({NUMBER})\s*(pt|px|mm|cm|in)?\s*$")
TRANSFORM = re.compile(rf"(translate|scale|rotate|matrix)\(([^)]*)\)")
FORBIDDEN = {
    "script": "FAIL",
    "foreignObject": "FAIL",
    "linearGradient": "WARN",
    "radialGradient": "WARN",
    "filter": "WARN",
}
MM_SINGLE, MM_DOUBLE = 89.0, 183.0


@dataclass(frozen=True)
class Finding:
    severity: str
    kind: str
    message: str


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_length(value: str | None) -> tuple[float, str] | None:
    match = LENGTH.match(value or "")
    if not match:
        return None
    number = float(match.group(1))
    if not math.isfinite(number):
        raise ValueError("SVG length must be finite")
    return number, match.group(2) or ""


def style_value(element: ET.Element, name: str) -> str | None:
    style = element.get("style") or ""
    for part in style.split(";"):
        key, _, value = part.partition(":")
        if key.strip() == name:
            return value.strip()
    return element.get(name)


Matrix = tuple[float, float, float, float, float, float]
IDENTITY: Matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def multiply(first: Matrix, second: Matrix) -> Matrix:
    """Return ``first x second`` for SVG ``[a b c d e f]`` matrices."""
    a1, b1, c1, d1, e1, f1 = first
    a2, b2, c2, d2, e2, f2 = second
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def transform_matrix(element: ET.Element) -> Matrix:
    """Parse the complete supported transform list; never ignore unknown syntax."""
    result = IDENTITY
    raw = element.get("transform") or ""
    cursor = 0
    for match in TRANSFORM.finditer(raw):
        if raw[cursor:match.start()].strip(" \t\n\r,"):
            raise ValueError("unsupported or malformed SVG transform")
        kind, args = match.groups()
        if re.sub(NUMBER, "", args).strip(" \t\n\r,"):
            raise ValueError("unsupported SVG transform arguments")
        n = [float(v) for v in re.findall(NUMBER, args)]
        if not all(math.isfinite(value) for value in n):
            raise ValueError("SVG transform values must be finite")
        if kind == "translate" and len(n) in (1, 2):
            local_matrix: Matrix = (1.0, 0.0, 0.0, 1.0, n[0], n[1] if len(n) == 2 else 0.0)
        elif kind == "scale" and len(n) in (1, 2):
            local_matrix = (n[0], 0.0, 0.0, n[1] if len(n) == 2 else n[0], 0.0, 0.0)
        elif kind == "rotate" and len(n) in (1, 3):
            cos, sin = math.cos(math.radians(n[0])), math.sin(math.radians(n[0]))
            local_matrix = (cos, sin, -sin, cos, 0.0, 0.0)
            if len(n) == 3:
                shift: Matrix = (1.0, 0.0, 0.0, 1.0, n[1], n[2])
                back: Matrix = (1.0, 0.0, 0.0, 1.0, -n[1], -n[2])
                local_matrix = multiply(multiply(shift, local_matrix), back)
        elif kind == "matrix" and len(n) == 6:
            local_matrix = (n[0], n[1], n[2], n[3], n[4], n[5])
        else:
            raise ValueError("unsupported SVG transform or argument count")
        result = multiply(result, local_matrix)
        if not all(math.isfinite(value) for value in result):
            raise ValueError("SVG transform arithmetic is non-finite")
        cursor = match.end()
    if raw[cursor:].strip(" \t\n\r,"):
        raise ValueError("unsupported or malformed SVG transform")
    return result


def matrix_scale(matrix: Matrix) -> float:
    """Isotropic scale factor (square root of |det|) of the linear part."""
    value = abs(matrix[0] * matrix[3] - matrix[1] * matrix[2]) ** 0.5
    if not math.isfinite(value) or value <= 0:
        raise ValueError("SVG text has a degenerate or non-finite transform")
    return value


def first_number(value: str | None) -> float | None:
    """First number of an SVG coordinate list such as ``"10 20 30"``."""
    found = re.findall(NUMBER, value or "")
    value = float(found[0]) if found else None
    if value is not None and not math.isfinite(value):
        raise ValueError("SVG coordinates must be finite")
    return value


def canvas_scale(root: ET.Element) -> tuple[float, float | None, bool]:
    """Return (points per user unit, width in pt or None, units_known)."""
    raw_view_box = root.get("viewBox") or ""
    if re.sub(NUMBER, "", raw_view_box).strip(" \t\n\r,"):
        raise ValueError("unsupported viewBox syntax")
    view_box = [float(n) for n in re.findall(NUMBER, raw_view_box)]
    if view_box and (len(view_box) != 4 or not all(math.isfinite(n) for n in view_box) or view_box[2] <= 0 or view_box[3] <= 0):
        raise ValueError("viewBox must have four finite values and positive dimensions")
    width = parse_length(root.get("width"))
    if width and width[0] <= 0:
        raise ValueError("SVG width must be positive")
    view_width = view_box[2] if len(view_box) == 4 and view_box[2] > 0 else None
    if width and PT_PER_UNIT.get(width[1]):
        width_pt = width[0] * PT_PER_UNIT[width[1]]
        # SVG user units are CSS px without a viewBox, regardless of the
        # physical unit used to declare the viewport width.
        unit_scale = width_pt / view_width if view_width else 0.75
        if view_width:
            height = parse_length(root.get("height"))
            if height and PT_PER_UNIT.get(height[1]):
                height_pt = height[0] * PT_PER_UNIT[height[1]]
                if not math.isfinite(height_pt) or height_pt <= 0:
                    raise ValueError("SVG height must be finite and positive")
                y_scale = height_pt / view_box[3]
                preserve = (root.get("preserveAspectRatio") or "xMidYMid meet").split()
                if preserve[0] == "none" or "slice" in preserve:
                    raise ValueError("non-uniform or cropped viewBox transforms require rendered inspection")
                unit_scale = min(unit_scale, y_scale)
        if not math.isfinite(width_pt) or not math.isfinite(unit_scale) or unit_scale <= 0:
            raise ValueError("SVG physical size/scale must be finite and positive")
        return unit_scale, width_pt, True
    if view_width:
        return 1.0, view_width, False  # unitless: assume 1 user unit = 1 pt
    return 1.0, None, False


def audit_svg(
    data: bytes,
    min_pt: float = 5.0,
    max_pt: float = 7.0,
    max_width_mm: float = MM_DOUBLE,
) -> dict[str, object]:
    findings: list[Finding] = []
    if any(not math.isfinite(value) or value <= 0 for value in (min_pt, max_pt, max_width_mm)) or max_pt < min_pt:
        return {"auditable": False, "error": "thresholds must be finite and positive; max_pt >= min_pt", "findings": []}
    lowered = data.lower()
    if b"<!doctype" in lowered or b"<!entity" in lowered:
        return {"auditable": False, "error": "DTD or entity declarations are not supported", "findings": []}
    try:
        root = ET.fromstring(data)  # nosec B314 - DTDs and entities rejected above
    except ET.ParseError as exc:
        return {"auditable": False, "error": f"not well-formed XML: {exc}", "findings": []}
    if local(root.tag) != "svg":
        return {"auditable": False, "error": "root element is not <svg>", "findings": []}

    try:
        unit_scale, width_pt, units_known = canvas_scale(root)
    except (TypeError, ValueError, OverflowError) as exc:
        return {"auditable": False, "error": str(exc), "findings": []}
    if not units_known:
        findings.append(
            Finding("WARN", "canvas.units", "width has no physical unit; assuming 1 user unit = 1 pt")
        )
    width_mm = width_pt * 25.4 / 72 if width_pt else None
    if width_mm is None:
        findings.append(Finding("WARN", "canvas.size", "no width or viewBox; final size unknown"))
    else:
        if width_mm > max_width_mm + 0.5:
            findings.append(
                Finding("FAIL", "canvas.width", f"width {width_mm:.1f} mm exceeds {max_width_mm:g} mm")
            )
        elif min(abs(width_mm - MM_SINGLE), abs(width_mm - MM_DOUBLE)) > 2.0:
            findings.append(
                Finding("WARN", "canvas.width", f"width {width_mm:.1f} mm is not 89 mm or 183 mm")
            )

    view_box = [float(n) for n in re.findall(NUMBER, root.get("viewBox") or "")]
    sizes: list[float] = []
    texts = 0

    def check_text(element: ET.Element, label: str, matrix: Matrix, font_size: float | None, anchor: bool) -> None:
        nonlocal texts
        texts += 1
        if font_size is None:
            findings.append(
                Finding("WARN", "text.size", f"font-size not set for {label[:30]!r}; SVG default is 16 units")
            )
        else:
            effective = font_size * matrix_scale(matrix) * unit_scale
            if not math.isfinite(effective) or effective <= 0:
                raise ValueError("effective SVG text size must be finite and positive")
            sizes.append(effective)
            if effective < min_pt - 1e-6:
                findings.append(Finding("FAIL", "text.small", f"{label[:30]!r} is {effective:.2f} pt (< {min_pt:g} pt)"))
            elif effective > max_pt + 1e-6:
                findings.append(Finding("WARN", "text.large", f"{label[:30]!r} is {effective:.2f} pt (> {max_pt:g} pt)"))
        if anchor and len(view_box) == 4:
            x, y = first_number(element.get("x")), first_number(element.get("y"))
            if x is not None and y is not None:
                px = matrix[0] * x + matrix[2] * y + matrix[4]
                py = matrix[1] * x + matrix[3] * y + matrix[5]
                if not (
                    view_box[0] <= px <= view_box[0] + view_box[2]
                    and view_box[1] <= py <= view_box[1] + view_box[3]
                ):
                    findings.append(Finding("FAIL", "text.off-canvas", f"{label[:30]!r} is anchored outside the viewBox"))

    def declared_size(element: ET.Element, inherited: float | None) -> float | None:
        raw_size = style_value(element, "font-size")
        if raw_size is None or raw_size == "inherit":
            return inherited
        length = parse_length(raw_size)
        if not length or length[0] <= 0:
            raise ValueError("unsupported or non-positive font-size")
        # CSS absolute units resolve to CSS px before the viewBox/element
        # transforms: e.g. 6pt is 8 user units, then final scale is applied.
        return length[0] * (PT_PER_UNIT[length[1]] / 0.75 if PT_PER_UNIT.get(length[1]) else 1.0)

    def walk(element: ET.Element, matrix: Matrix, font_size: float | None, parent_tag: str) -> None:
        tag = local(element.tag)
        if tag in {"style", "use"} or style_value(element, "transform") != element.get("transform"):
            raise ValueError("CSS styles, CSS transforms and reused elements require separate rendered inspection")
        if tag in FORBIDDEN:
            findings.append(Finding(FORBIDDEN[tag], "forbidden", f"<{tag}> is not allowed in a production schematic"))
        for key, value in element.attrib.items():
            if local(key) == "href" and not (value.startswith("#") or value.startswith("data:")):
                findings.append(Finding("FAIL", "external-ref", f"external reference: {value[:60]}"))
        matrix = multiply(matrix, transform_matrix(element))
        own_size = declared_size(element, font_size)
        label = "".join(element.itertext()).strip()
        if tag == "text" and label:
            # A size set only on descendant tspans is checked per tspan below.
            sized_children = any(
                local(child.tag) == "tspan" and style_value(child, "font-size") for child in element.iter()
            )
            if own_size is not None or not sized_children:
                check_text(element, label, matrix, own_size, anchor=True)
        elif tag == "tspan" and label:
            if parent_tag != "text":
                check_text(element, label, matrix, own_size, anchor=True)
            elif style_value(element, "font-size"):
                check_text(element, label, matrix, own_size, anchor=False)
        for child in element:
            walk(child, matrix, own_size, tag)

    try:
        walk(root, IDENTITY, None, "")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        return {"auditable": False, "error": str(exc), "findings": [asdict(f) for f in findings]}
    if not texts:
        findings.append(Finding("WARN", "text.none", "no <text> found; text may be outlined, which journals reject"))
    return {
        "auditable": units_known and bool(texts) and len(sizes) == texts,
        "error": "Final physical text size could not be audited for all text elements" if not (units_known and bool(texts) and len(sizes) == texts) else None,
        "width_mm": width_mm,
        "text_count": texts,
        "minimum_found_pt": min(sizes) if sizes else None,
        "maximum_found_pt": max(sizes) if sizes else None,
        "thresholds": {"min_pt": min_pt, "max_pt": max_pt, "max_width_mm": max_width_mm},
        "findings": [asdict(f) for f in findings],
    }


def verdict(result: dict[str, object]) -> str:
    if not result["auditable"]:
        return "NOT AUDITABLE"
    severities = {f["severity"] for f in result["findings"]}  # type: ignore[index]
    return "FAIL" if "FAIL" in severities else "PASS WITH WARNINGS" if "WARN" in severities else "PASS"


def render_text(path: Path, result: dict[str, object]) -> str:
    lines = ["Academic Figure SVG Schematic Audit", f"svg: {path}"]
    if not result["auditable"]:
        lines.append(f"error: {result['error']}")
    else:
        width = result["width_mm"]
        lines.append(f"width: {width:.1f} mm" if width else "width: unknown")
        lines.append(f"text elements: {result['text_count']}")
        if result["minimum_found_pt"] is not None:
            lines.append(f"text size: {result['minimum_found_pt']:.2f} to {result['maximum_found_pt']:.2f} pt")
        for f in result["findings"]:  # type: ignore[union-attr]
            lines.append(f"[{f['severity']}] {f['kind']}: {f['message']}")
    lines.append(f"verdict: {verdict(result)}")
    lines.append("note: overlaps, crossings and outlined text are not detected; inspect the render at final size")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path, help="SVG schematic")
    parser.add_argument("--min-pt", type=float, default=5.0, help="minimum text size in points")
    parser.add_argument("--max-pt", type=float, default=7.0, help="maximum ordinary text size in points")
    parser.add_argument("--max-width-mm", type=float, default=MM_DOUBLE, help="maximum canvas width in mm")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if any(not math.isfinite(value) or value <= 0 for value in (args.min_pt, args.max_pt, args.max_width_mm)) or args.max_pt < args.min_pt:
        print("error: thresholds must be finite and positive and --max-pt >= --min-pt", file=sys.stderr)
        return 2
    try:
        data = args.svg.read_bytes()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        result = audit_svg(data, args.min_pt, args.max_pt, args.max_width_mm)
    except Exception as exc:
        print(f"error: SVG audit failed: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"svg": str(args.svg), "verdict": verdict(result), **result}, indent=2, ensure_ascii=False, allow_nan=False))
    else:
        print(render_text(args.svg, result))
    if not result["auditable"]:
        return 2
    return 1 if verdict(result) == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
