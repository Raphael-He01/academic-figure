import csv
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ('ggplot2', 'patchwork', 'ggdist', 'ggrepel', 'colorspace', 'ragg',
            'svglite', 'readxl', 'scales', 'farver', 'systemfonts', 'viridisLite', 'jsonlite')


class PipelineTest(unittest.TestCase):
    def test_scaffold_to_exports(self):
        r = shutil.which('Rscript')
        if not r:
            self.skipTest('Rscript unavailable')
        expr = 'quit(status=if(all(vapply(c(' + ','.join('"'+p+'"' for p in PACKAGES) + '),requireNamespace,logical(1),quietly=TRUE))) 0 else 1)'
        if subprocess.run([r, '--vanilla', '-e', expr], capture_output=True).returncode:
            self.skipTest('full R plotting dependencies unavailable')
        with tempfile.TemporaryDirectory(prefix='figure pipeline ') as tmp:
            project = Path(tmp) / 'project'
            scaffold = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/scaffold_project.py'), str(project)],
                check=True, capture_output=True, text=True, encoding='utf-8',
            )
            self.assertTrue((project / 'Academic-Figure.Rproj').is_file())
            preview = project / 'output/previews/academic_figure_example_preview.png'
            self.assertIn(str(preview), scaffold.stdout)
            (project / 'output/qa').mkdir(parents=True)
            subprocess.run([r, '--vanilla', 'R/run_example.R'], cwd=project, check=True, capture_output=True, timeout=120)
            self.assertTrue(preview.is_file())
            component_check = '''source("R/plot_forest.R"); source("R/plot_ternary.R")
              stopifnot(inherits(plot_forest(data.frame(label="A", estimate=1, lower=0, upper=2)), "ggplot"))
              stopifnot(inherits(try(plot_forest(data.frame(label="A", estimate=1, lower=2, upper=3)), silent=TRUE), "try-error"))
              stopifnot(inherits(plot_ternary_points(data.frame(a=.2,b=.3,c=.5)), "ggplot"))
              stopifnot(inherits(try(plot_ternary_points(data.frame(a=1,b=1,c=1)), silent=TRUE), "try-error"))
              source("R/plot_spectra_network.R")
              s <- data.frame(sample_id=c("a","a"), wavelength=c(1,2), value=c(2,3))
              stopifnot(inherits(plot_spectra(s, "nm", "response"), "ggplot"))
              stopifnot(inherits(try(plot_spectra(rbind(s,s), "nm", "response"), silent=TRUE), "try-error"))
              n <- data.frame(id=c("a","b"), x=c(0,1), y=c(0,1)); e <- data.frame(from="a", to="b")
              p <- plot_network(n,e,"x","y"); stopifnot(inherits(p,"ggplot"), length(linked_zoom(p,c(0,.5),c(0,.5))) == 2)
              stopifnot(inherits(try(plot_network(n,data.frame(from="a",to="missing"),"x","y"), silent=TRUE), "try-error"))'''
            subprocess.run([r, '--vanilla', '-e', component_check], cwd=project, check=True, capture_output=True, timeout=30)
            palette_check = '''source("R/figure_config.R"); source("R/qa_palette.R")
              one <- run_palette_qa(figure_config(groups="A"), tempfile())
              stopifnot(all(is.na(one$minimum_pairwise_delta_e_2000)),
                        all(one$screen == "NOT APPLICABLE"))'''
            subprocess.run([r, '--vanilla', '-e', palette_check], cwd=project, check=True, capture_output=True, timeout=30)
            qa_dir = project / 'output/qa'
            with (qa_dir / 'palette_accessibility.csv').open(encoding='utf-8', newline='') as f:
                swatches = list(csv.DictReader(f))
            simulations = {'Original', 'Deuteranopia', 'Protanopia', 'Tritanopia', 'Grayscale'}
            self.assertEqual({row['simulation'] for row in swatches}, simulations)
            self.assertTrue(all(float(row['label_contrast_ratio']) >= 4.5 for row in swatches))
            self.assertTrue(all(row['label_color'] == '#000000' for row in swatches
                                if row['simulation'] == 'Original'))
            with (qa_dir / 'heatmap_palette_accessibility.csv').open(encoding='utf-8', newline='') as f:
                self.assertEqual({row['simulation'] for row in csv.DictReader(f)}, simulations)
            manifest = project / 'output/qa/export_manifest.csv'
            with manifest.open(encoding='utf-8', newline='') as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 4)
            for row in rows:
                self.assertTrue((project / row['path']).is_file())
                self.assertEqual(row['acceptance'], 'pending')
                self.assertEqual(row['palette_id'], 'rose_mist')
