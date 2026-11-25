"""Offline release regressions. Optional tools produce explicit skips."""
import csv,importlib.util,json,os,re,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*args,cwd=ROOT): return subprocess.run(args,cwd=cwd,capture_output=True,text=True)
class Release(unittest.TestCase):
 def test_skill_frontmatter(self):
  text=(ROOT/'SKILL.md').read_text()
  self.assertTrue(text.startswith('---\n'))
  front=text.split('---',2)[1]
  self.assertRegex(front,r'(?m)^name: academic-figure$')
  self.assertRegex(front,r'(?m)^description: .+')
 def test_links(self):
  for f in [p for p in ROOT.rglob('*.md') if not any(part in {'artifacts', '.git', '.Rproj.user'} for part in p.relative_to(ROOT).parts)]:
   for s in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)',f.read_text()):
    if re.match(r'[A-Za-z][\w+.-]*:',s):continue
    target=(f.parent/s.split('#')[0]).resolve()
    self.assertTrue(target.is_relative_to(ROOT),str(f)+': '+s)
    self.assertTrue(target.exists(),str(f)+': '+s)
    if '#' in s and target.suffix == '.md':
     anchor=s.split('#',1)[1]
     headings=[]
     for line in target.read_text().splitlines():
      if re.match(r'^#{1,6} ',line):
       heading=re.sub(r'^#+\s+','',line).lower().strip()
       headings.append(re.sub(r'[^\w\- ]','',heading).replace(' ','-'))
     if anchor:self.assertIn(anchor,headings,str(f)+': '+s)
 def test_scaffold_no_overwrite_and_space_path(self):
  with tempfile.TemporaryDirectory() as d:
   q=Path(d)/'project with spaces'
   self.assertEqual(run(sys.executable,'-B','scripts/scaffold_project.py',str(q)).returncode,0)
   p=q/'R/figure_config.R';p.write_text('user-owned')
   self.assertEqual(run(sys.executable,'-B','scripts/scaffold_project.py',str(q)).returncode,3)
   self.assertEqual(p.read_text(),'user-owned')
   self.assertEqual(json.loads((q/'data/palettes/catalog.json').read_text()),json.loads((ROOT/'assets/palettes/catalog.json').read_text()))
 def test_alignment(self):
  x=run(sys.executable,'-B','scripts/qa/audit_panel_alignment.py','--self-test');self.assertEqual(x.returncode,0,x.stderr)
 def test_colour_cli(self):
  x=run(sys.executable,'-B','scripts/palette_catalog.py','--show','rose_mist');self.assertEqual(x.returncode,0,x.stderr)
  self.assertEqual(run(sys.executable,'-B','scripts/palette_catalog.py','--show','no-such-card').returncode,2)
 def test_palette_binding_in_R(self):
  if not shutil.which('Rscript'):self.skipTest('Rscript unavailable')
  probe=run('Rscript','--vanilla','-e','quit(status=if(requireNamespace("jsonlite",quietly=TRUE)) 0 else 2)')
  if probe.returncode:self.skipTest('jsonlite unavailable')
  code='source("R/figure_config.R"); a<-figure_config(); stopifnot(a$palette$id=="rose_mist",identical(unname(a$group_colors),c("#C289A0","#527F94","#A5B59A"))); b<-figure_config(groups=c("B","A"));stopifnot(identical(names(b$group_colors),c("B","A"))); stopifnot(inherits(try(figure_config("bad"),silent=TRUE),"try-error")); stopifnot(inherits(try(resolve_colour_card("rose_mist",letters[1:4]),silent=TRUE),"try-error"));cat("binding verified")'
  x=run('Rscript','--vanilla','-e',code,cwd=ROOT/'assets/r-template');self.assertEqual(x.returncode,0,x.stderr)
 def test_palette_browser(self):
  if not shutil.which('node'):self.skipTest('Node unavailable')
  x=run('node','scripts/test_palette_catalog.cjs');self.assertEqual(x.returncode,0,x.stderr)
 def test_qa_normal_bad_and_no_dependency(self):
  with tempfile.TemporaryDirectory() as d:
   q=Path(d); good=q/'good.svg';bad=q/'bad.svg'
   good.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="89mm" height="60mm" viewBox="0 0 89 60"><text x="10" y="20" font-size="2.1">Test</text></svg>')
   bad.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="200mm" height="60mm" viewBox="0 0 200 60"><text x="250" y="20" font-size="2.1">Outside</text></svg>')
   for p,expected in [(good,0),(bad,1)]:
    x=run(sys.executable,'-B','scripts/qa/audit_svg_schematic.py',str(p),'--json');self.assertEqual(x.returncode,expected,x.stdout+x.stderr)
   broken=q/'broken.pdf';broken.write_bytes(b'not a pdf')
   self.assertNotEqual(run(sys.executable,'-B','scripts/qa/audit_pdf_fonts.py',str(broken),'--json').returncode,0)
   self.assertEqual(run(sys.executable,'-I','-S',str(ROOT/'scripts/qa/audit_pdf_fonts.py'),str(broken)).returncode,2)
 def test_pdf_unembedded_and_collisions(self):
  if importlib.util.find_spec('pymupdf') is None:self.skipTest('PyMuPDF unavailable')
  import pymupdf as fitz
  with tempfile.TemporaryDirectory() as d:
   for name,overlap,expected in [('clean',False,0),('overlap',True,1)]:
    q=Path(d)/(name+'.pdf');doc=fitz.open();p=doc.new_page();p.insert_text((50,70),'First text',fontsize=12);p.insert_text((50,70 if overlap else 110),'Other text',fontsize=12);doc.save(q);doc.close()
    x=run(sys.executable,'-B','scripts/qa/audit_figure_collisions.py',str(q),'--json');self.assertEqual(x.returncode,expected,x.stdout+x.stderr)
    self.assertEqual(run(sys.executable,'-B','scripts/qa/audit_pdf_fonts.py',str(q),'--json').returncode,1)
 def test_missing_export_status(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'manifest.csv';p.write_text('path,format,font_embedding,file_check,acceptance\nmissing.pdf,PDF,pending,pending,pending\n')
   x=run(sys.executable,'-B','scripts/reconcile_export_status.py',str(p));self.assertEqual(x.returncode,1,x.stderr)
   with p.open(newline='') as f: self.assertEqual(list(csv.DictReader(f))[0]['acceptance'],'failed')
 def test_status_hash_paths_and_invalidation(self):
  import hashlib
  with tempfile.TemporaryDirectory() as d:
   project=Path(d)/'project with spaces'; qa=project/'output/qa'; qa.mkdir(parents=True)
   svg=project/'plot.svg'; svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="89mm" height="60mm" viewBox="0 0 89 60"><rect width="10" height="10"/></svg>')
   digest=hashlib.sha256(svg.read_bytes()).hexdigest()
   manifest=qa/'export_manifest.csv'
   manifest.write_text('path,width_mm,height_mm,scientific_review,visual_review,review_sha256\nplot.svg,89,60,pass,pass,'+digest+'\n')
   command=[sys.executable,'-B',str(ROOT/'scripts/reconcile_export_status.py'),str(manifest)]
   x=run(*command,cwd=Path(d));self.assertEqual(x.returncode,0,x.stderr+x.stdout)
   with manifest.open(newline='') as f: row=list(csv.DictReader(f))[0]
   self.assertEqual(row['visual_review'],'pass'); self.assertEqual(row['acceptance'],'pending')
   svg.write_text(svg.read_text().replace('width="10"','width="11"'))
   x=run(*command,cwd=Path(d));self.assertEqual(x.returncode,0,x.stderr)
   with manifest.open(newline='') as f: row=list(csv.DictReader(f))[0]
   self.assertEqual(row['visual_review'],'pending');self.assertEqual(row['scientific_review'],'pending')
   self.assertNotEqual(row['file_sha256'],digest)
 def test_bad_manifest_is_not_modified(self):
  with tempfile.TemporaryDirectory() as d:
   manifest=Path(d)/'manifest.csv'; manifest.write_text('path,width_mm\nmissing.svg,NaN\n')
   before=manifest.read_bytes()
   x=run(sys.executable,'-B','scripts/reconcile_export_status.py',str(manifest))
   self.assertEqual(x.returncode,2);self.assertEqual(manifest.read_bytes(),before)
 def test_dimension_mismatch_fails(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);svg=root/'plot.svg';svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="89mm" height="60mm" viewBox="0 0 89 60"/>')
   manifest=root/'manifest.csv';manifest.write_text('path,width_mm,height_mm\nplot.svg,100,60\n')
   x=run(sys.executable,'-B','scripts/reconcile_export_status.py',str(manifest))
   self.assertEqual(x.returncode,1,x.stdout+x.stderr)
   with manifest.open(newline='') as f: self.assertEqual(list(csv.DictReader(f))[0]['file_check'],'failed')
 def test_pdf_geometry_checks_without_poppler(self):
  if importlib.util.find_spec('pymupdf') is None:
   self.skipTest('PyMuPDF unavailable')
  import pymupdf
  with tempfile.TemporaryDirectory() as d:
   path = Path(d) / 'figure.pdf'
   with pymupdf.open() as document:
    document.new_page(width=72, height=144)
    document.save(path)
   script = ROOT / 'scripts/verify_exports.py'
   env = {**os.environ, 'PATH': ''}
   for width, code in [('25.4', 0), ('30', 1)]:
    result = subprocess.run(
     [sys.executable, '-B', str(script), '--width-mm', width, str(path)],
     capture_output=True, text=True, env=env,
    )
    self.assertEqual(result.returncode, code, result.stdout+result.stderr)
   result = subprocess.run(
    [sys.executable, '-I', '-S', str(script), '--width-mm', '25.4', str(path)],
    capture_output=True, text=True, env=env,
   )
   self.assertEqual(result.returncode, 2, result.stdout+result.stderr)
   self.assertIn('NOT AUDITABLE', result.stdout)
 def test_colour_review_raster(self):
  if importlib.util.find_spec('pymupdf') is None or not shutil.which('Rscript'):self.skipTest('Rscript or PyMuPDF unavailable')
  probe=run('Rscript','--vanilla','-e','quit(status=if(all(vapply(c("colorspace","jsonlite"),requireNamespace,logical(1),quietly=TRUE))) 0 else 2)')
  if probe.returncode:self.skipTest('R colours packages unavailable')
  import pymupdf,hashlib
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);image=root/'small.png';data=bytes([255,0,0,0,255,0,0,0,255,255,255,255])
   pymupdf.Pixmap(pymupdf.csRGB,2,2,data,False).save(image)
   output=root/'review';x=run(sys.executable,'-B','scripts/render_colour_review.py',str(image),str(output))
   self.assertEqual(x.returncode,0,x.stdout+x.stderr)
   record=json.loads((output/'review.json').read_text());self.assertEqual(record['input_sha256'],hashlib.sha256(image.read_bytes()).hexdigest())
   for file in record['files_sha256']:
    pix=pymupdf.Pixmap(str(output/file));self.assertEqual((pix.width,pix.height),(2,2))
    self.assertEqual(hashlib.sha256((output/file).read_bytes()).hexdigest(),record['files_sha256'][file])
   grey=pymupdf.Pixmap(str(output/'grayscale.png')).samples
   self.assertTrue(all(grey[i]==grey[i+1]==grey[i+2] for i in range(0,len(grey),3)))
   before=(output/'review.json').read_bytes()
   self.assertEqual(run(sys.executable,'-B','scripts/render_colour_review.py',str(image),str(output)).returncode,2)
   self.assertEqual(before,(output/'review.json').read_bytes())
if __name__=='__main__':unittest.main(verbosity=2)
