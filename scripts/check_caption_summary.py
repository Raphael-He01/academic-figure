#!/usr/bin/env python3
"""Compare declared n and mean with an explicitly selected numeric CSV column."""
import argparse
import csv
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from pathlib import Path
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv_file', type=Path)
    p.add_argument('column')
    p.add_argument('facts', type=Path, help='JSON with integer n, string mean and integer decimals')
    a = p.parse_args()
    try:
        facts = json.loads(a.facts.read_text(encoding='utf-8'))
        if type(facts['n']) is not int or type(facts['decimals']) is not int or not 0 <= facts['decimals'] <= 10 or not isinstance(facts['mean'], str):
            raise ValueError('invalid facts: require integer n, string mean, decimals 0..10')
        declared = Decimal(facts['mean'])
        if not declared.is_finite(): raise ValueError('mean must be finite')
        values = []
        with a.csv_file.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or reader.fieldnames.count(a.column) != 1:
                raise ValueError('column missing or duplicated')
            for row in reader:
                if None in row or row[a.column] is None or not row[a.column].strip():
                    raise ValueError('malformed row or missing value; decide exclusions before checking')
                value = Decimal(row[a.column].strip())
                if not value.is_finite(): raise ValueError('nonfinite value')
                values.append(value)
        if not values: raise ValueError('no observations')
        mean = (sum(values) / len(values)).quantize(Decimal(1).scaleb(-facts['decimals']), rounding=ROUND_HALF_UP)
        ok = len(values) == facts['n'] and mean == declared
        print(json.dumps({'status': 'match' if ok else 'mismatch', 'n': len(values), 'mean': str(mean),
                          'scope': 'Selected rows only; independence, exclusions and scientific interpretation not verified.'}))
        return 0 if ok else 1
    except (OSError, ValueError, KeyError, TypeError, InvalidOperation) as exc:
        print('summary check failed: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__': sys.exit(main())
