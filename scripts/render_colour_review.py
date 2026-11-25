#!/usr/bin/env python3
"""Create full-raster CVD/gray review copies using installed R colorspace.

Requires PyMuPDF, Rscript, jsonlite and colorspace; never installs anything.
Copies are diagnostic only, never replacements for the original artwork.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path, help='New, empty review directory')
    args = parser.parse_args()
    try:
        import pymupdf
    except ImportError:
        print('NOT AUDITABLE: install optional PyMuPDF for raster review', file=sys.stderr)
        return 2
    executable = shutil.which('Rscript')
    if executable is None:
        print('NOT AUDITABLE: Rscript unavailable', file=sys.stderr)
        return 2
    if args.output.exists():
        print('Refusing an existing output directory', file=sys.stderr)
        return 2
    try:
        input_bytes = args.input.read_bytes()
        pix = pymupdf.Pixmap(input_bytes)
        if pix.alpha or pix.n != 3 or pix.width * pix.height > 20_000_000:
            raise ValueError('Supply an opaque RGB raster of at most 20 million pixels')
        pixels = pix.samples
        unique = sorted(set(pixels[i:i+3] for i in range(0, len(pixels), 3)))
        with tempfile.TemporaryDirectory(prefix='figure-colour-review-') as d:
            directory = Path(d)
            source = directory/'palette.json'
            result = directory/'transformed.json'
            source.write_text(json.dumps(['#'+c.hex() for c in unique]), encoding='utf-8')
            script = directory/'simulate.R'
            script.write_text('''args <- commandArgs(trailingOnly=TRUE)
for (p in c("jsonlite", "colorspace")) if (!requireNamespace(p,quietly=TRUE)) stop("Missing R dependency: ",p)
x <- jsonlite::fromJSON(args[1])
y <- list(deutan=colorspace::deutan(x),protan=colorspace::protan(x),tritan=colorspace::tritan(x),grayscale=colorspace::desaturate(x))
jsonlite::write_json(y,args[2],auto_unbox=FALSE)
''', encoding='utf-8')
            process = subprocess.run([executable,'--vanilla',str(script),str(source),str(result)], capture_output=True, text=True, timeout=60)
            if process.returncode:
                raise ValueError('NOT AUDITABLE: R colour simulation failed: '+process.stderr[-500:])
            variants = json.loads(result.read_text(encoding='utf-8'))
        # Validate transformations before creating the deliverable directory.
        for colours in variants.values():
            if len(colours) != len(unique):
                raise ValueError('Colour lookup length mismatch')
            for value in colours:
                if len(bytes.fromhex(value.lstrip('#'))) != 3:
                    raise ValueError('Invalid transformed colour')
        args.output.mkdir(parents=True)
        files = {}
        for name, colours in variants.items():
            lookup = dict(zip(unique,[bytes.fromhex(c.lstrip('#')) for c in colours]))
            data = b''.join(lookup[pixels[i:i+3]] for i in range(0,len(pixels),3))
            output = args.output/(name+'.png')
            pymupdf.Pixmap(pymupdf.csRGB,pix.width,pix.height,data,False).save(output)
            files[output.name] = hashlib.sha256(output.read_bytes()).hexdigest()
        record = dict(input_name=args.input.name,input_sha256=hashlib.sha256(input_bytes).hexdigest(),
                      width_px=pix.width,height_px=pix.height,files_sha256=files,
                      method='R colorspace full-raster RGB transformation; severity defaults to package simulation',
                      acceptance='pending visual review; no universal accessibility certification')
        (args.output/'review.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(record,indent=2))
        return 0
    except (OSError,ValueError,subprocess.TimeoutExpired) as error:
        print(str(error),file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
