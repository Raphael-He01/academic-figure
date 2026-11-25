#!/usr/bin/env python3
"""Original PyMuPDF-based audit of font-program embedding in PDF resources.

This checks object-level evidence, not typography, glyph correctness, visual
quality, accessibility, or the semantic correctness of a scientific figure.
No network access, automatic installation, or external PDF utilities are used.

Exit codes: 0 = all discovered fonts have embedding evidence;
1 = at least one font is explicitly not embedded;
2 = unavailable dependency, invalid input, or an inconclusive audit.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


REF = re.compile(r"(\d+)\s+(\d+)\s+R")
CHARPROC = re.compile(r"/([^\s<>\[\]()%/]+)\s+(\d+)\s+(\d+)\s+R")
PROGRAM_KEYS = ("FontFile", "FontFile2", "FontFile3")
DESCRIPTOR_SUBTYPES = {"Type1", "MMType1", "TrueType", "CIDFontType0", "CIDFontType2"}
LIMITATIONS = [
    "Inspects fonts reachable through each page's font resources, including Form XObjects.",
    "A nonempty font-program or Type3 glyph stream is embedding evidence only; its content is not validated.",
    "Does not verify text semantics, glyph coverage, visual appearance, or scientific correctness.",
    "No auditable fonts (including an outline-only PDF) is inconclusive, not a pass.",
]


class AuditError(Exception):
    """An input or object structure cannot be reliably audited."""


def reference(value: str) -> int:
    match = REF.fullmatch(value.strip())
    if not match or int(match.group(1)) <= 0:
        raise AuditError(f"Invalid indirect object reference: {value!r}")
    return int(match.group(1))


def reference_array(value: str) -> list[int]:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        raise AuditError("DescendantFonts is not a reference array")
    body, position, refs = value[1:-1], 0, []
    while position < len(body):
        if body[position].isspace():
            position += 1
            continue
        match = REF.match(body, position)
        if not match:
            raise AuditError("DescendantFonts contains an unsupported or invalid entry")
        refs.append(reference(match.group(0)))
        position = match.end()
    if not refs:
        raise AuditError("DescendantFonts is empty")
    return refs


def charproc_dictionary(value: str) -> list[tuple[str, int]]:
    """Read the restricted name-to-stream-reference form required by CharProcs."""
    value = value.strip()
    if not (value.startswith("<<") and value.endswith(">>")):
        raise AuditError("CharProcs is not a dictionary")
    body, position, entries = value[2:-2], 0, []
    while position < len(body):
        if body[position].isspace():
            position += 1
            continue
        match = CHARPROC.match(body, position)
        if not match:
            raise AuditError("CharProcs contains an unsupported or invalid entry")
        entries.append((match.group(1), reference(f"{match.group(2)} {match.group(3)} R")))
        position = match.end()
    if not entries:
        raise AuditError("CharProcs has no auditable glyph streams")
    return entries


class FontAuditor:
    def __init__(self, document: Any):
        self.document = document

    def check_xref(self, xref: int) -> None:
        if not 0 < xref < self.document.xref_length():
            raise AuditError(f"Object {xref} is outside the PDF cross-reference table")

    def key(self, xref: int, name: str) -> tuple[str, str]:
        self.check_xref(xref)
        return self.document.xref_get_key(xref, name)

    def stream_evidence(self, xref: int, source: str) -> dict[str, Any]:
        self.check_xref(xref)
        if not self.document.xref_is_stream(xref):
            raise AuditError(f"{source} refers to object {xref}, which is not a stream")
        data = self.document.xref_stream(xref)
        if not data:
            raise AuditError(f"{source} stream object {xref} is empty or unreadable")
        return {"source": source, "stream_xref": xref, "decoded_bytes": len(data)}

    def audit(self, xref: int, ancestors: tuple[int, ...] = ()) -> dict[str, Any]:
        result: dict[str, Any] = {"xref": xref, "status": "unknown", "evidence": []}
        try:
            if xref in ancestors or len(ancestors) >= 16:
                raise AuditError("Cyclic or excessively nested font references")
            subtype_type, subtype_value = self.key(xref, "Subtype")
            if subtype_type != "name":
                raise AuditError("Font object has no valid Subtype name")
            subtype = subtype_value.removeprefix("/")
            result["subtype"] = subtype
            result["base_font"] = self.key(xref, "BaseFont")[1]
            if subtype == "Type0":
                self.audit_type0(xref, result, ancestors)
            elif subtype == "Type3":
                self.audit_type3(xref, result)
            elif subtype in DESCRIPTOR_SUBTYPES:
                self.audit_descriptor(xref, result)
            else:
                raise AuditError(f"Unsupported font subtype: {subtype}")
        except Exception as exc:
            result["status"] = "unknown"
            result["reason"] = f"{type(exc).__name__}: {exc}"
        return result

    def audit_type0(self, xref: int, result: dict[str, Any], ancestors: tuple[int, ...]) -> None:
        kind, value = self.key(xref, "DescendantFonts")
        if kind == "xref":
            array_xref = reference(value)
            self.check_xref(array_xref)
            value = self.document.xref_object(array_xref).strip()
            kind = "array" if value.startswith("[") else "invalid"
            result["descendant_array_xref"] = array_xref
        if kind != "array":
            raise AuditError("Type0 font has no readable DescendantFonts array")
        refs = reference_array(value)
        children = [self.audit(ref, (*ancestors, xref)) for ref in refs]
        result["descendants"] = children
        if any(child.get("subtype") not in {"CIDFontType0", "CIDFontType2"} for child in children):
            raise AuditError("Type0 descendant is not a supported CID font")
        statuses = {child["status"] for child in children}
        if "not_embedded" in statuses:
            result.update(status="not_embedded", reason="A CID descendant has no embedded font program")
        elif "unknown" in statuses:
            result.update(status="unknown", reason="A CID descendant could not be audited")
        else:
            result.update(status="embedded", reason="All CID descendants have font-program stream evidence")

    def audit_descriptor(self, xref: int, result: dict[str, Any]) -> None:
        kind, value = self.key(xref, "FontDescriptor")
        if kind == "null":
            result.update(status="not_embedded", reason="FontDescriptor is absent; Base14 fonts are not exempt")
            return
        if kind == "xref":
            owner, prefix = reference(value), ""
            self.check_xref(owner)
            result["descriptor_xref"] = owner
            if (not self.document.xref_object(owner).strip().startswith("<<")
                    or self.document.xref_is_stream(owner)):
                raise AuditError("FontDescriptor does not refer to a dictionary object")
        elif kind == "dict":
            owner, prefix = xref, "FontDescriptor/"
            result["descriptor_inline"] = True
        else:
            raise AuditError("FontDescriptor is neither a dictionary nor an indirect reference")
        descriptor_type, descriptor_value = self.key(owner, prefix + "Type")
        if descriptor_type != "null" and (descriptor_type != "name" or descriptor_value != "/FontDescriptor"):
            raise AuditError("FontDescriptor dictionary has an invalid Type")
        for name in PROGRAM_KEYS:
            stream_kind, stream_value = self.key(owner, prefix + name)
            if stream_kind == "null":
                continue
            if stream_kind != "xref":
                raise AuditError(f"{name} is not an indirect stream reference")
            result["evidence"].append(self.stream_evidence(reference(stream_value), name))
        if result["evidence"]:
            result.update(status="embedded", reason="FontDescriptor references a nonempty font-program stream")
        else:
            result.update(status="not_embedded", reason="FontDescriptor has no FontFile, FontFile2, or FontFile3")

    def audit_type3(self, xref: int, result: dict[str, Any]) -> None:
        kind, value = self.key(xref, "CharProcs")
        if kind == "xref":
            owner = reference(value)
            self.check_xref(owner)
            result["charprocs_xref"] = owner
            entries = []
            for name in self.document.xref_get_keys(owner):
                stream_kind, stream_value = self.key(owner, name)
                if stream_kind != "xref":
                    raise AuditError(f"Type3 CharProcs entry {name!r} is not a stream reference")
                entries.append((name, reference(stream_value)))
        elif kind == "dict":
            result["charprocs_inline"] = True
            entries = charproc_dictionary(value)
        else:
            raise AuditError("Type3 font has no readable CharProcs dictionary")
        if not entries:
            raise AuditError("Type3 font has no auditable glyph streams")
        for name, stream_xref in entries:
            result["evidence"].append(self.stream_evidence(stream_xref, f"CharProcs/{name}"))
        result.update(status="embedded", reason="All Type3 CharProcs entries have nonempty glyph-stream evidence")


def inspect_pdf(pdf_path: Path, pymupdf: Any, report: dict[str, Any]) -> int:
    with pymupdf.open(str(pdf_path)) as document:
        if not document.is_pdf:
            raise AuditError("Input is not a PDF document")
        if document.needs_pass:
            raise AuditError("Encrypted PDF requires a password; this CLI does not accept passwords")
        report["page_count"] = document.page_count
        report["repaired"] = bool(document.is_repaired)
        if not document.page_count:
            raise AuditError("PDF contains no pages")
        auditor = FontAuditor(document)
        fonts: dict[int, dict[str, Any]] = {}
        for page_number in range(document.page_count):
            page = document.load_page(page_number)
            width, height = float(page.rect.width), float(page.rect.height)
            if not all(math.isfinite(value) and value > 0 for value in (width, height)):
                raise AuditError(f"Page {page_number + 1} has invalid dimensions")
            report["pages"].append({"page": page_number + 1, "width_pt": width,
                                    "height_pt": height, "rotation": page.rotation})
            for font in document.get_page_fonts(page_number, full=True):
                xref = int(font[0])
                if xref not in fonts:
                    fonts[xref] = auditor.audit(xref)
                    fonts[xref]["uses"] = []
                use = {"page": page_number + 1, "resource_name": str(font[4]),
                       "reported_base_font": str(font[3]), "referencer_xref": int(font[6])}
                if use not in fonts[xref]["uses"]:
                    fonts[xref]["uses"].append(use)
        report["fonts"] = list(fonts.values())
        report["font_count"] = len(fonts)
        statuses = {font["status"] for font in fonts.values()}
        if "not_embedded" in statuses:
            report.update(status="fail", message="At least one font is explicitly not embedded")
            return 1
        if document.is_repaired:
            report.update(status="inconclusive", message="PyMuPDF repaired the input; a clean parse cannot be confirmed")
            return 2
        if not fonts:
            report.update(status="inconclusive", message="No auditable font resources were found")
            return 2
        if "unknown" in statuses:
            report.update(status="inconclusive", message="Embedding could not be determined for at least one font")
            return 2
        report.update(status="pass", message="Every discovered font has object-level embedding evidence")
        return 0


def same_file(first: Path, second: Path) -> bool:
    if first.resolve() == second.resolve():
        return True
    return first.exists() and second.exists() and first.samefile(second)


def print_font(font: dict[str, Any], indent: str = "  ") -> None:
    print(f"{indent}Font {font['xref']} ({font.get('subtype', '?')}, {font.get('base_font', '?')}): "
          f"{font['status']} — {font.get('reason', '')}")
    for item in font["evidence"]:
        print(f"{indent}  {item['source']} -> stream {item['stream_xref']}, "
              f"{item['decoded_bytes']} decoded bytes")
    for child in font.get("descendants", []):
        print_font(child, indent + "  ")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf", type=Path, help="PDF file to audit")
    parser.add_argument("--json", action="store_true", help="Print a JSON report instead of human-readable output")
    parser.add_argument("--json-out", type=Path, metavar="PATH", help="Also write JSON to PATH (parent must already exist)")
    args = parser.parse_args(argv)
    report: dict[str, Any] = {"schema_version": 1, "input": str(args.pdf.absolute()),
                              "status": "inconclusive", "message": "Audit did not complete",
                              "page_count": None, "pages": [], "font_count": 0, "fonts": [],
                              "limitations": LIMITATIONS}
    output_allowed = True
    try:
        if args.json_out is not None and same_file(args.pdf, args.json_out):
            output_allowed = False
            raise AuditError("--json-out must not overwrite the input PDF, including symlink or hard-link aliases")
        if not args.pdf.is_file():
            raise AuditError(f"Input is not an existing regular file: {args.pdf}")
        try:
            import pymupdf
        except ImportError as exc:
            raise AuditError("PyMuPDF is unavailable. Install it explicitly for this interpreter with "
                             f"{sys.executable} -m pip install PyMuPDF. No installation was attempted. ({exc})") from exc
        report["pymupdf_version"] = getattr(pymupdf, "__version__", "unknown")
        exit_code = inspect_pdf(args.pdf, pymupdf, report)
    except Exception as exc:
        exit_code = 2
        report.update(status="inconclusive", message=f"{type(exc).__name__}: {exc}")
    report["exit_code"] = exit_code
    if args.json_out is not None and output_allowed:
        try:
            # Recheck immediately before writing, including existing hard links.
            if same_file(args.pdf, args.json_out):
                raise AuditError("--json-out now aliases the input PDF; refusing to overwrite it")
            args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        except Exception as exc:
            exit_code = 2
            report.update(status="inconclusive", exit_code=2,
                          message=f"Cannot write JSON report: {type(exc).__name__}: {exc}")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    else:
        print(f"{report['status'].upper()}: {report['message']}")
        print(f"Pages: {report['page_count']}; distinct font resources: {report['font_count']}")
        for page in report["pages"]:
            print(f"  Page {page['page']}: {page['width_pt']:g} x {page['height_pt']:g} pt; rotation {page['rotation']}")
        for font in report["fonts"]:
            print_font(font)
        print("Embedding evidence only; semantic and visual quality were not checked.")
        if exit_code == 2:
            print(report["message"], file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
