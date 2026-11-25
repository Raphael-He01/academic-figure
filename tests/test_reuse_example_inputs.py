"""Exercise first-run and revision behaviour via the R scaffold's normal entrypoint."""
import csv
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_r_pipeline import PACKAGES, ROOT


class ReuseExampleInputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = shutil.which("Rscript")
        if not cls.r:
            raise unittest.SkipTest("Rscript unavailable")
        packages = ", ".join(f'"{pkg}"' for pkg in PACKAGES)
        probe = f'quit(status=as.integer(!all(vapply(c({packages}), requireNamespace, logical(1), quietly=TRUE))))'
        if subprocess.run([cls.r, "--vanilla", "-e", probe], capture_output=True).returncode:
            raise unittest.SkipTest("Full R plotting dependencies unavailable")

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="resume existing figure ")
        self.addCleanup(tmp.cleanup)
        self.project = Path(tmp.name) / "demo project"
        subprocess.run([sys.executable, str(ROOT / "scripts/scaffold_project.py"), str(self.project)],
                       check=True, capture_output=True)
        self.data = self.project / "data"
        self.call_r("-e", 'source("R/figure_config.R"); source("R/generate_example_data.R"); '
                          'generate_example_data(figure_config())')

    def call_r(self, *args, expect_success=True):
        result = subprocess.run([self.r, "--vanilla", *args], cwd=self.project,
                                text=True, capture_output=True, timeout=120)
        if expect_success:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stderr + result.stdout)
        return result.stderr + result.stdout

    def digests(self):
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.data.glob("simulated_*.csv")}

    def test_reuse_reordered_inputs_and_reconcile_endpoint(self):
        self.call_r("-e", '''
            for (dataset in c("trend", "distribution")) {
              file <- sprintf("data/simulated_%s.csv", dataset)
              x <- read.csv(file)
              x$response[x$day == 28 & x$group == "Control"] <- 20 + x$replicate[x$day == 28 & x$group == "Control"]
              write.csv(x[rev(seq_len(nrow(x))), ], file, row.names=FALSE)
            }
        ''')
        before = self.digests()
        self.assertIn("Reusing", self.call_r("R/run_example.R"))
        self.assertEqual(self.digests(), before)
        with (self.project / "output/qa/trend_summary.csv").open(newline="") as src:
            row = next(r for r in csv.DictReader(src) if r["day"] == "28" and r["group"] == "Control")
        self.assertEqual(float(row["mean"]), 24.5)
        self.assertIn("24.5", (self.project / "docs/example_caption_and_results.md").read_text())

        output = self.project / "output/png/academic_figure_example.png"
        previous_image = output.read_bytes()
        self.call_r("-e", '''
            file <- "data/simulated_distribution.csv"
            x <- read.csv(file)
            x$response[1] <- x$response[1] + 1
            write.csv(x, file, row.names=FALSE)
        ''')
        inconsistent = self.digests()
        self.assertIn("endpoint_matches_trend", self.call_r("R/run_example.R", expect_success=False))
        self.assertEqual(self.digests(), inconsistent)
        self.assertEqual(output.read_bytes(), previous_image)
        for path in self.data.glob("simulated_*.csv"):
            path.unlink()
        qa = self.project / "output/qa"
        manifest = qa / "export_manifest.csv"
        previous_manifest = manifest.read_bytes()
        self.assertIn("Incomplete example input set", self.call_r("R/run_example.R", expect_success=False))
        self.assertEqual(self.digests(), {})
        self.assertEqual(output.read_bytes(), previous_image)
        self.assertEqual(manifest.read_bytes(), previous_manifest)
        manifest.unlink()
        (qa / "data_validation.txt").unlink()
        self.assertIn("Start a new scaffold", self.call_r("R/run_example.R", expect_success=False))
        self.assertEqual(self.digests(), {})
        self.assertEqual(output.read_bytes(), previous_image)

    def test_partial_set_survives_resume_without_fabricated_rows(self):
        (self.data / "simulated_heatmap.csv").unlink()
        remaining = self.digests()
        failure = self.call_r("R/run_example.R", expect_success=False)
        self.assertIn("simulated_heatmap.csv", failure)
        self.assertEqual(self.digests(), remaining)
        self.assertFalse((self.project / "output/qa/export_manifest.csv").exists())
