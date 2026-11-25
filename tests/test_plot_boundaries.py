from pathlib import Path
import shutil
import subprocess
import unittest


TEMPLATE = Path(__file__).resolve().parents[1] / 'assets/r-template'


class PlotBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = shutil.which('Rscript')
        if not cls.r:
            raise unittest.SkipTest('Rscript unavailable')
        probe = subprocess.run([cls.r, '--vanilla', '-e',
                                'quit(status = !requireNamespace("ggplot2", quietly=TRUE))'])
        if probe.returncode:
            raise unittest.SkipTest('ggplot2 unavailable')

    def run_r(self, code):
        result = subprocess.run([self.r, '--vanilla', '-'], input=code,
                                cwd=TEMPLATE, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_cartesian_zoom_retains_scale_and_original(self):
        self.run_r('''
            library(ggplot2)
            source("R/plot_spectra_network.R")
            p <- plot_spectra(data.frame(sample_id="A", wavelength=c(100,1000,10000),
                                         value=c(.1,.4,.8)), "nm", "Signal") + scale_x_log10()
            z <- linked_zoom(p, c(100,1000), c(.1,.4))
            panel <- ggplot_build(z$detail)$layout$panel_params[[1]]
            box <- layer_data(z$overview, 2)
            stopifnot(is.null(z$detail$coordinates$ratio), identical(p$coordinates$limits$x,NULL),
                      identical(z$overview$coordinates$limits, p$coordinates$limits),
                      isTRUE(all.equal(panel$x.range,c(2,3))),
                      isTRUE(all.equal(panel$y.range,c(.1,.4))),
                      isTRUE(all.equal(c(box$xmin,box$xmax),panel$x.range)),
                      nrow(layer_data(z$detail, 1))==3)
            fixed <- p + coord_fixed(ratio=2, clip="off")
            detail <- linked_zoom(fixed, c(100,1000), c(.1,.4))$detail
            stopifnot(identical(detail$coordinates$ratio, fixed$coordinates$ratio),
                      identical(detail$coordinates$clip,"off"))
            flipped <- linked_zoom(p + coord_flip(), c(100,1000), c(.1,.4))$detail
            panel <- ggplot_build(flipped)$layout$panel_params[[1]]
            stopifnot(inherits(flipped$coordinates,"CoordFlip"),
                      isTRUE(all.equal(panel$x.range,c(.1,.4))),
                      isTRUE(all.equal(panel$y.range,c(2,3))))
        ''')

    def test_projected_and_polar_views_need_specialized_locator(self):
        self.run_r('''
            library(ggplot2)
            source("R/plot_spectra_network.R")
            p <- ggplot(mtcars, aes(wt, mpg)) + geom_point()
            expect_locator_error <- function(p) {
              error <- tryCatch({linked_zoom(p, c(2,4), c(15,25)); NULL}, error=identity)
              stopifnot(inherits(error,"error"),grepl("locator",conditionMessage(error)))
            }
            expect_locator_error(p + coord_polar())
            # Exercise the projection guard even on installations without sf.
            p$coordinates <- ggproto(NULL, CoordSf)
            expect_locator_error(p)
        ''')

    def test_ternary_requires_a_finite_scalar_closure_tolerance(self):
        self.run_r('''
            source("R/plot_ternary.R")
            mix <- data.frame(a=.5,b=.25,c=.25)
            stopifnot(inherits(plot_ternary_points(mix,0),"ggplot"))
            rounded <- data.frame(a=.33,b=.33,c=.33)
            stopifnot(inherits(plot_ternary_points(rounded,.011),"ggplot"),
                      inherits(try(plot_ternary_points(rounded,.001),silent=TRUE),"try-error"))
            invalid <- list(Inf,-Inf,NaN,NA_real_,-.1,1,"0",numeric(),c(.01,.02))
            for (tol in invalid) {
              e <- tryCatch({plot_ternary_points(mix,tol); NULL},error=identity)
              stopifnot(inherits(e,"error"),grepl("tolerance",conditionMessage(e)))
            }
            wrong <- data.frame(a=.7,b=.7,c=.7)
            stopifnot(inherits(try(plot_ternary_points(wrong,Inf),silent=TRUE),"try-error"))
        ''')
