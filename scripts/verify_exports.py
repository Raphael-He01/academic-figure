#!/usr/bin/env python3
"""Perform non-visual structural checks on common scientific-figure exports."""

from __future__ import annotations

import argparse
import math
import re
import shutil
import struct
import subprocess
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--width-mm", type=float)
    parser.add_argument("--height-mm", type=float)
    parser.add_argument("--tolerance-mm", type=float, default=0.6)
    args = parser.parse_args()
    for key in ("width_mm", "height_mm"):
        value = getattr(args, key)
        if value is not None and (not math.isfinite(value) or value <= 0):
            parser.error(f"--{key.replace('_', '-')} must be finite and positive")
    if not math.isfinite(args.tolerance_mm) or args.tolerance_mm < 0:
        parser.error("--tolerance-mm must be finite and nonnegative")
    return args


def run(command: list[str]) -> str:
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    return result.stdout


def check_expected(name: str, width_mm: float | None, height_mm: float | None, args: argparse.Namespace) -> list[str]:
    messages: list[str] = []
    for axis, measured, expected in (("width", width_mm, args.width_mm), ("height", height_mm, args.height_mm)):
        if expected is None:
            continue
        if measured is None:
            messages.append(f"{name} {axis}: FAIL (physical dimension unavailable)")
        else:
            ok = math.isclose(measured, expected, rel_tol=0, abs_tol=args.tolerance_mm)
            messages.append(f"{name} {axis} {measured:.2f} mm: {'PASS' if ok else 'FAIL'}")
    return messages


def pdf_geometry(path: Path) -> tuple[int, float, float] | None:
    try:
        import pymupdf
    except ImportError:
        if not shutil.which("pdfinfo"):
            return None
        output = run(["pdfinfo", str(path)])
        size = re.search(r"Page size:\s+([0-9.]+) x ([0-9.]+) pts", output)
        pages = re.search(r"Pages:\s+(\d+)", output)
        if not size or not pages:
            raise ValueError("could not read the page count and dimensions")
        return int(pages[1]), float(size[1]), float(size[2])
    with pymupdf.open(path) as document:
        if not document.is_pdf or document.needs_pass or document.is_repaired or not len(document):
            raise ValueError("PDF requires a clean, unencrypted parse with at least one page")
        rect = document[0].rect
        return len(document), float(rect.width), float(rect.height)


def check_pdf(path: Path, args: argparse.Namespace) -> tuple[list[str], bool | None]:
    data = path.read_bytes()
    ok = data.startswith(b"%PDF-") and b"%%EOF" in data[-2048:]
    messages = [f"PDF signature/trailer: {'PASS' if ok else 'FAIL'}"]
    if not ok:
        return messages, False
    try:
        geometry = pdf_geometry(path)
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        return messages + [f"PDF geometry: FAIL ({exc})"], False
    if geometry is None:
        messages.append("PDF dimensions/pages: NOT AUDITABLE (PyMuPDF and pdfinfo unavailable)")
        ok = None
    else:
        pages, width_pt, height_pt = geometry
        ok = pages == 1
        messages.append(f"PDF single page: {'PASS' if ok else 'FAIL'}")
        messages.extend(check_expected("PDF", width_pt * 25.4 / 72, height_pt * 25.4 / 72, args))

    if shutil.which("pdffonts"):
        rows = [row for row in run(["pdffonts", str(path)]).splitlines()[2:] if row.strip()]
        embedded = bool(rows) and all(
            len(row.split()) >= 8 and row.split()[-5].lower() == "yes"
            for row in rows
        )
        messages.append(f"PDF fonts embedded: {'PASS' if embedded else 'FAIL'}")
        if not embedded:
            ok = False
    else:
        messages.append("PDF font embedding: SKIP (pdffonts unavailable)")
    return messages, ok


def length_to_mm(value: str | None) -> float | None:
    if not value:
        return None
    match = re.fullmatch(r"\s*(\d+(?:\.\d*)?|\.\d+)\s*(mm|cm|in|pt|px)?\s*", value, re.ASCII)
    if not match:
        return None
    number = float(match.group(1))
    if not math.isfinite(number) or number <= 0:
        return None
    unit = match.group(2) or "px"
    return number * {"mm": 1.0, "cm": 10.0, "in": 25.4, "pt": 25.4 / 72, "px": 25.4 / 96}[unit]


def check_svg(path: Path, args: argparse.Namespace) -> tuple[list[str], bool]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [f"SVG XML parse: FAIL ({exc})"], False
    is_svg = root.tag.endswith("svg")
    messages = [f"SVG XML/root: {'PASS' if is_svg else 'FAIL'}"]
    messages.extend(check_expected("SVG", length_to_mm(root.get("width")), length_to_mm(root.get("height")), args))
    has_vector = any(element.tag.endswith(("path", "line", "rect", "circle", "polygon")) for element in root.iter())
    messages.append(f"SVG vector elements: {'PASS' if has_vector else 'FAIL'}")
    return messages, is_svg and has_vector


def check_png(path: Path, args: argparse.Namespace) -> tuple[list[str], bool]:
    data = path.read_bytes()
    ok = data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 33
    messages = [f"PNG signature: {'PASS' if ok else 'FAIL'}"]
    if ok:
        cursor = 8
        width = height = 0
        width_mm = height_mm = None
        seen_ihdr = False
        seen_iend = False
        chunk_index = 0
        while cursor + 12 <= len(data):
            length = struct.unpack(">I", data[cursor:cursor + 4])[0]
            chunk = data[cursor + 4:cursor + 8]
            chunk_end = cursor + 12 + length
            if chunk_end > len(data):
                ok = False
                messages.append("PNG chunk bounds: FAIL")
                break
            payload = data[cursor + 8:cursor + 8 + length]
            stored_crc = struct.unpack(">I", data[cursor + 8 + length:chunk_end])[0]
            actual_crc = zlib.crc32(chunk)
            actual_crc = zlib.crc32(payload, actual_crc) & 0xFFFFFFFF
            if stored_crc != actual_crc:
                ok = False
                messages.append(f"PNG CRC for {chunk.decode('ascii', 'replace')}: FAIL")
                break
            if chunk_index == 0:
                if chunk != b"IHDR" or length != 13:
                    ok = False
                    messages.append("PNG IHDR: FAIL")
                    break
                width, height = struct.unpack(">II", payload[:8])
                seen_ihdr = width > 0 and height > 0
            if chunk == b"pHYs" and len(payload) == 9 and payload[8] == 1:
                xppm, yppm = struct.unpack(">II", payload[:8])
                width_mm = width / xppm * 1000 if xppm else None
                height_mm = height / yppm * 1000 if yppm else None
                messages.append(f"PNG density: {xppm * 0.0254:.1f} x {yppm * 0.0254:.1f} dpi")
            if chunk == b"IEND":
                seen_iend = length == 0
                cursor = chunk_end
                break
            cursor = chunk_end
            chunk_index += 1
        if not seen_ihdr or not seen_iend or cursor != len(data):
            ok = False
            messages.append("PNG complete chunk stream/IEND: FAIL")
        else:
            messages.append("PNG complete chunk stream/IEND: PASS")
            messages.append(f"PNG pixels: {width} x {height}")
        if width_mm is None or height_mm is None:
            if args.width_mm is not None or args.height_mm is not None:
                ok = False
                messages.append("PNG physical dimensions: FAIL (pHYs unavailable)")
            else:
                messages.append("PNG physical dimensions: SKIP (pHYs unavailable)")
        else:
            dimension_messages = check_expected("PNG", width_mm, height_mm, args)
            messages.extend(dimension_messages)
            ok = ok and not any(message.endswith("FAIL") for message in dimension_messages)
    return messages, ok


def check_tiff(path: Path, args: argparse.Namespace) -> tuple[list[str], bool]:
    data = path.read_bytes()
    if len(data) < 8 or data[:2] not in (b"II", b"MM"):
        return ["TIFF signature: FAIL"], False
    endian = "<" if data[:2] == b"II" else ">"
    magic = struct.unpack(endian + "H", data[2:4])[0]
    if magic != 42:
        return ["TIFF classic signature: FAIL (BigTIFF or invalid TIFF is not supported)"], False

    ifd_offset = struct.unpack(endian + "I", data[4:8])[0]
    if ifd_offset + 2 > len(data):
        return ["TIFF first IFD: FAIL"], False
    entry_count = struct.unpack(endian + "H", data[ifd_offset:ifd_offset + 2])[0]
    type_sizes = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8}
    tags: dict[int, tuple[int, int, bytes]] = {}
    for index in range(entry_count):
        start = ifd_offset + 2 + index * 12
        entry = data[start:start + 12]
        if len(entry) != 12:
            return ["TIFF IFD entries: FAIL"], False
        tag, value_type, count = struct.unpack(endian + "HHI", entry[:8])
        size = type_sizes.get(value_type, 0) * count
        if not size:
            continue
        if size <= 4:
            raw = entry[8:8 + size]
        else:
            value_offset = struct.unpack(endian + "I", entry[8:12])[0]
            raw = data[value_offset:value_offset + size]
        if len(raw) == size:
            tags[tag] = (value_type, count, raw)

    def scalar(tag: int) -> float | None:
        item = tags.get(tag)
        if item is None:
            return None
        value_type, _count, raw = item
        if value_type == 3:
            return float(struct.unpack(endian + "H", raw[:2])[0])
        if value_type == 4:
            return float(struct.unpack(endian + "I", raw[:4])[0])
        if value_type == 5:
            numerator, denominator = struct.unpack(endian + "II", raw[:8])
            return numerator / denominator if denominator else None
        return None

    def integer_values(tag: int) -> list[int]:
        item = tags.get(tag)
        if item is None:
            return []
        value_type, count, raw = item
        if value_type == 3:
            return list(struct.unpack(endian + ("H" * count), raw))
        if value_type == 4:
            return list(struct.unpack(endian + ("I" * count), raw))
        return []

    width = scalar(256)
    height = scalar(257)
    x_resolution = scalar(282)
    y_resolution = scalar(283)
    resolution_unit = scalar(296)
    compression = scalar(259)
    ok = width is not None and height is not None
    messages = ["TIFF signature/IFD: PASS" if ok else "TIFF dimensions: FAIL"]
    if ok:
        messages.append(f"TIFF pixels: {int(width)} x {int(height)}")
    if compression is not None:
        names = {1: "none", 5: "LZW", 8: "Deflate"}
        messages.append(f"TIFF compression: {names.get(int(compression), int(compression))}")

    strip_offsets = integer_values(273)
    strip_byte_counts = integer_values(279)
    tile_offsets = integer_values(324)
    tile_byte_counts = integer_values(325)
    if strip_offsets or strip_byte_counts:
        storage_kind = "strip"
        offsets, byte_counts = strip_offsets, strip_byte_counts
    elif tile_offsets or tile_byte_counts:
        storage_kind = "tile"
        offsets, byte_counts = tile_offsets, tile_byte_counts
    else:
        storage_kind = "pixel"
        offsets, byte_counts = [], []

    storage_ok = (
        bool(offsets)
        and len(offsets) == len(byte_counts)
        and all(offset >= 8 for offset in offsets)
        and all(byte_count > 0 for byte_count in byte_counts)
        and all(
            offset + byte_count <= len(data)
            for offset, byte_count in zip(offsets, byte_counts)
        )
    )
    messages.append(
        f"TIFF {storage_kind} data segments: "
        f"{'PASS' if storage_ok else 'FAIL'}"
        + (f" ({len(offsets)} segments)" if storage_ok else "")
    )
    ok = ok and storage_ok

    width_mm = height_mm = None
    if width is not None and height is not None and x_resolution and y_resolution:
        if resolution_unit == 2:
            width_mm = width / x_resolution * 25.4
            height_mm = height / y_resolution * 25.4
            messages.append(f"TIFF density: {x_resolution:.1f} x {y_resolution:.1f} dpi")
        elif resolution_unit == 3:
            width_mm = width / x_resolution * 10
            height_mm = height / y_resolution * 10
            messages.append(
                f"TIFF density: {x_resolution:.1f} x {y_resolution:.1f} pixels/cm"
            )
    if width_mm is None or height_mm is None:
        messages.append("TIFF physical dimensions: SKIP (resolution tags unavailable)")
    messages.extend(check_expected("TIFF", width_mm, height_mm, args))
    return messages, ok


def main() -> int:
    args = parse_args()
    passed = True
    incomplete = False
    handlers = {".pdf": check_pdf, ".svg": check_svg, ".png": check_png, ".tif": check_tiff, ".tiff": check_tiff}
    for raw_path in args.files:
        path = raw_path.expanduser().resolve()
        print(f"\n{path}")
        if not path.is_file() or path.stat().st_size == 0:
            print("File exists and is non-empty: FAIL")
            passed = False
            continue
        print(f"File exists and is non-empty: PASS ({path.stat().st_size} bytes)")
        handler = handlers.get(path.suffix.lower())
        if handler is None:
            print(f"Unsupported extension: {path.suffix}")
            passed = False
            continue
        messages, file_ok = handler(path, args)
        for message in messages:
            print(message)
        if any(message.endswith("FAIL") or ": FAIL (" in message for message in messages):
            file_ok = False
        incomplete = incomplete or file_ok is None
        passed = passed and file_ok is not False
    return 1 if not passed else 2 if incomplete else 0


if __name__ == "__main__":
    raise SystemExit(main())
