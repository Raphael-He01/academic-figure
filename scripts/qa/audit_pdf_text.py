#!/usr/bin/env python3
# Adapted from nature-figure (Apache-2.0). QA-only helper; it never renders a figure.
# Modified: rewritten around PyMuPDF text-span sizes and incomplete-extraction checks; replaces the upstream standard-library stream parser and its parser-specific caveats.
"""Check final PDF text-span sizes reported by PyMuPDF.

This is a final-span size aid, not a PDF conformance validator or a measurement
of glyph ink height. PyMuPDF resolves page content and Form XObject transforms;
its reported span size is the metric tested here. Parser/decode warnings, pages
without extractable text, Type 3 fonts, unsupported writing modes and invalid
geometry make the audit incomplete and exit 2. Text in raster images, outlined
glyphs, visual legibility, anisotropic glyph compression, clipping, and hidden
text require separate final-size visual inspection. Even PASS is scoped to
extractable text spans, never a guarantee about all visible lettering.

PyMuPDF is imported only when auditing a PDF. Optional dependency installation:
``python3 -m pip install --user PyMuPDF``.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


LIMITATIONS = [
    "Checks PyMuPDF final text-span size; does not measure actual glyph ink height or anisotropic glyph compression.",
    "Rasterized and outlined lettering is not measured; inspect the final export visually.",
    "Clipping, visibility, collisions and font embedding are outside this helper's scope.",
]


@dataclass(frozen=True)
class TextRun:
    page: int
    font: str
    size_pt: float
    text: str


def _finite(values: Any) -> bool:
    try:
        return all(math.isfinite(float(value)) for value in values)
    except (TypeError, ValueError, OverflowError):
        return False


def audit_pdf(data: bytes, minimum_pt: float = 5.0) -> dict[str, object]:
    """Audit final text spans; any extraction/decode uncertainty blocks PASS."""
    if not math.isfinite(minimum_pt) or minimum_pt <= 0:
        raise ValueError("minimum_pt must be finite and positive")
    try:
        import pymupdf as fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required. Install with: python3 -m pip install --user PyMuPDF") from exc

    warnings: list[str] = []
    runs: list[TextRun] = []
    page_count = 0
    display_errors = fitz.TOOLS.mupdf_display_errors()
    display_warnings = fitz.TOOLS.mupdf_display_warnings()
    fitz.TOOLS.mupdf_display_errors(False)
    fitz.TOOLS.mupdf_display_warnings(False)
    fitz.TOOLS.mupdf_warnings(reset=True)
    try:
        with fitz.open(stream=data, filetype="pdf") as document:
            if document.needs_pass:
                raise ValueError("encrypted PDF requires a password")
            page_count = document.page_count
            if not page_count:
                warnings.append("PDF contains no pages")
            # Force stream decoding, including Form XObjects; a damaged/unknown
            # filter must not disappear silently because another page has text.
            for xref in range(1, document.xref_length()):
                if document.xref_is_stream(xref):
                    try:
                        document.xref_stream(xref)
                    except Exception as exc:
                        warnings.append(f"stream xref {xref} could not be decoded: {exc}")
            for page_index, page in enumerate(document, 1):
                before = len(runs)
                if not _finite(page.rect) or page.rect.width <= 0 or page.rect.height <= 0:
                    warnings.append(f"page {page_index} has invalid final dimensions")
                fonts = page.get_fonts(full=True)
                if any(str(font[2]).lower() == "type3" for font in fonts):
                    warnings.append(f"page {page_index} contains Type 3 font glyphs with unsupported size semantics")
                text_dict = page.get_text("dict", flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)
                for block in text_dict.get("blocks", []):
                    if block.get("type") != 0:
                        continue
                    for line in block.get("lines", []):
                        direction = line.get("dir")
                        if not direction or len(direction) != 2 or not _finite(direction) or not math.isclose(math.hypot(*direction), 1.0, abs_tol=1e-4):
                            warnings.append(f"page {page_index} has unknown or invalid text direction/transform")
                        if line.get("wmode", 0) != 0:
                            warnings.append(f"page {page_index} has unsupported vertical writing mode")
                        for span in line.get("spans", []):
                            text = str(span.get("text", ""))
                            if not text.strip():
                                continue
                            size = float(span.get("size", float("nan")))
                            bbox = span.get("bbox", ())
                            if not math.isfinite(size) or size <= 0 or len(bbox) != 4 or not _finite(bbox):
                                warnings.append(f"page {page_index} has a span with unknown size/transform")
                                continue
                            if "\ufffd" in text or "\x00" in text:
                                warnings.append(f"page {page_index} has undecodable text characters")
                            runs.append(TextRun(page=page_index, font=str(span.get("font", "")), size_pt=size, text=text[:120]))
                if before == len(runs):
                    warnings.append(f"page {page_index} has no extractable nonempty text spans; visible lettering cannot be certified")
    except Exception as exc:
        warnings.append(f"PDF extraction failed: {exc}")
    finally:
        parser_warnings = fitz.TOOLS.mupdf_warnings(reset=True)
        fitz.TOOLS.mupdf_display_errors(display_errors)
        fitz.TOOLS.mupdf_display_warnings(display_warnings)
        if parser_warnings:
            warnings.append(f"MuPDF parser/decode diagnostics: {parser_warnings}")

    warnings = list(dict.fromkeys(warnings))
    below = [run for run in runs if run.size_pt < minimum_pt]
    auditable = bool(runs) and not warnings
    verdict = "NOT AUDITABLE" if not auditable else "FAIL" if below else "PASS"
    return {
        "auditable": auditable,
        "verdict": verdict,
        "scope": "PyMuPDF final extractable text-span sizes only",
        "page_count": page_count,
        "minimum_required_pt": minimum_pt,
        "minimum_found_pt": min((run.size_pt for run in runs), default=None),
        "text_run_count": len(runs),
        "below_minimum_count": len(below),
        "below_minimum": [asdict(run) for run in below],
        "warnings": warnings,
        "limitations": LIMITATIONS,
    }


def render_text(path: Path, result: dict[str, object]) -> str:
    lines = ["Academic Figure PDF Text-Span Audit", f"pdf: {path}",
             f"minimum required: {result['minimum_required_pt']:g} pt",
             f"scope: {result['scope']}", f"text spans: {result['text_run_count']}"]
    if result["minimum_found_pt"] is not None:
        lines.append(f"minimum found: {result['minimum_found_pt']:g} pt")
    for run in result["below_minimum"]:
        lines.append(f"[FAIL] page {run['page']}: {run['font']} {run['size_pt']:g} pt — {run['text']!r}")
    for warning in result["warnings"]:
        lines.append(f"[INCOMPLETE] {warning}")
    lines.append(f"verdict: {result['verdict']}")
    for limitation in LIMITATIONS:
        lines.append(f"note: {limitation}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="exported PDF figure")
    parser.add_argument("--min-pt", type=float, default=5.0, help="minimum final span size in points")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not math.isfinite(args.min_pt) or args.min_pt <= 0:
        print("error: --min-pt must be finite and positive", file=sys.stderr)
        return 2
    try:
        data = args.pdf.read_bytes()
        if b"%PDF-" not in data[:1024]:
            raise ValueError(f"not a PDF file: {args.pdf}")
        result = audit_pdf(data, minimum_pt=args.min_pt)
        print(json.dumps({"pdf": str(args.pdf), **result}, indent=2, ensure_ascii=False, allow_nan=False) if args.json else render_text(args.pdf, result))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not result["auditable"]:
        return 2
    return 1 if result["below_minimum_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
