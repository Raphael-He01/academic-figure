#!/usr/bin/env python3
"""Read-only CSV structural profiling; no scientific meaning is inferred."""
import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path


def profile(path, keys=()):
    path = Path(path)
    data = path.read_bytes()
    text = data.decode('utf-8-sig')
    reader = csv.reader(text.splitlines(keepends=True), strict=True)
    header = next(reader, None)
    if not header or any(not name.strip() for name in header) or len(set(header)) != len(header):
        raise ValueError('CSV requires unique, nonempty column names')
    missing_keys = set(keys) - set(header)
    if missing_keys:
        raise ValueError('unknown key columns: ' + ', '.join(sorted(missing_keys)))
    columns = [[] for _ in header]
    key_counts = Counter()
    incomplete_keys = 0
    n = 0
    for row in reader:
        if len(row) != len(header):
            raise ValueError(f'row ending at line {reader.line_num}: expected {len(header)} fields, got {len(row)}')
        n += 1
        for col, value in zip(columns, row):
            col.append(value.strip())
        if keys:
            values = tuple(row[header.index(k)].strip() for k in keys)
            if any(not v for v in values):
                incomplete_keys += 1
            else:
                key_counts[values] += 1
    result = []
    for name, values in zip(header, columns):
        present = [v for v in values if v]
        numeric = nonfinite = 0
        for value in present:
            try:
                number = float(value)
                numeric += 1
                nonfinite += not math.isfinite(number)
            except ValueError:
                pass
        result.append({'name': name, 'empty': len(values) - len(present),
                       'distinct_nonempty': len(set(present)), 'numeric_parseable': numeric,
                       'nonfinite_numeric': nonfinite, 'meaning': 'unconfirmed', 'unit': 'unconfirmed'})
    return {'input_sha256': hashlib.sha256(data).hexdigest(), 'rows': n, 'columns': result,
            'key_columns': list(keys), 'incomplete_key_rows': incomplete_keys if keys else None,
            'duplicate_complete_key_rows': sum(v - 1 for v in key_counts.values()) if keys else None,
            'limitations': 'Empty means blank only; sentinel values, units, pairing and scientific meaning require confirmation.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_file')
    parser.add_argument('--key', action='append', default=[], help='confirmed key column; repeat for composite keys')
    args = parser.parse_args()
    try:
        print(json.dumps(profile(args.csv_file, args.key), ensure_ascii=False, indent=2, allow_nan=False))
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        print(f'profile failed: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
