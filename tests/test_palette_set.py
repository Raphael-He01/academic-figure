from pathlib import Path
import shutil
import subprocess
import unittest

TEMPLATE = Path(__file__).resolve().parents[1] / "assets/r-template"


class SetStyleTest(unittest.TestCase):
    def test_reordered_subset_keeps_the_marks_of_the_full_figure_set(self):
        r = shutil.which("Rscript")
        if not r:
            self.skipTest("Rscript unavailable")
        deps = 'quit(status=as.integer(!all(vapply(c("ggplot2","jsonlite"),requireNamespace,logical(1),quietly=TRUE))))'
        if subprocess.run([r, "--vanilla", "-e", deps], capture_output=True).returncode:
            self.skipTest("ggplot2 or jsonlite unavailable")
        script = """
            source("R/figure_config.R")
            source("R/figure_style.R")
            all_groups <- c("control", "north", "south")
            original <- figure_config(groups = all_groups)
            shown <- c("south", "north")
            subset <- figure_config(groups = shown, set_groups = all_groups)
            stopifnot(identical(subset$palette$mapping, original$palette$mapping))
            d <- data.frame(i = 1:2, value = 1:2, group = shown)
            p <- ggplot2::ggplot(d, ggplot2::aes(i, value, colour = group, shape = group)) +
                 ggplot2::geom_point() + group_color_scale(subset) + group_shape_scale(subset)
            marks <- ggplot2::layer_data(p)
            stopifnot(identical(marks$colour, unname(original$group_colors[shown])),
                      identical(as.numeric(marks$shape), unname(original$group_shapes[shown])),
                      identical(subset$group_linetypes, original$group_linetypes[shown]),
                      inherits(try(figure_config(groups="new", set_groups=all_groups), silent=TRUE),
                               "try-error"))
        """
        run = subprocess.run([r, "--vanilla", "-"], input=script, text=True, capture_output=True, cwd=TEMPLATE)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
