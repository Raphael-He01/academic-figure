"""Numerical and drawing checks for the scaffold's weighted state field."""
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("Rscript"), "Rscript unavailable")
class StateMassTest(unittest.TestCase):
    def run_r(self, code):
        preamble = 'source("assets/r-template/R/plot_state_mass.R")\n'
        result = subprocess.run(["Rscript", "--vanilla", "-"], cwd=ROOT,
                                input=preamble + code, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_complete_schedule_tails_and_exact_branch(self):
        self.run_r("""
          d <- data.frame(time=c(rep(2,6),9,9), state=c(-3,-1,0,1,2,3,-1,-1),
                          weight=c(1,2,3,4,5,5,1e308,1e308), particle=c(1:6,1:2))
          r <- state_mass_table(d, c(9,2,4), c(-1,0,1.5,2))
          eq <- function(x,y) isTRUE(all.equal(x,y,tolerance=1e-14))
          stopifnot(eq(r$cells$mass,c(.1,.35,.25,NA,NA,NA,1,0,0)),
                    eq(r$summary$time,c(2,4,9)), eq(r$summary$n,c(6,0,2)),
                    eq(r$summary$above,c(.7,NA,0)), eq(r$summary$below_range,c(.05,NA,0)),
                    eq(r$summary$above_range,c(.25,NA,0)), eq(r$summary$ess,c(5,NA,2)))
          rev_r <- state_mass_table(d[nrow(d):1,], c(2,4,9), c(-1,0,1.5,2))
          stopifnot(eq(r, rev_r))
          # A narrower display window preserves branch probabilities and exposes omitted mass.
          crop <- state_mass_table(d, c(2,4,9), c(.25,.75))
          stopifnot(eq(crop$summary$above, r$summary$above),
                    eq(crop$cells$mass,c(0,NA,0)), eq(crop$summary$below_range,c(.3,NA,1)))
        """)

    def test_invalid_inputs_are_explicit(self):
        self.run_r("""
          d <- data.frame(time=c(1,1),state=c(0,1),weight=c(1,2), particle=c(1,2))
          bad <- function(x) inherits(try(x, silent=TRUE), "try-error")
          stopifnot(bad(state_mass_table(transform(d,weight=0), 1, c(0,1))),
                    bad(state_mass_table(transform(d,weight=c(1,-1)), 1, c(0,1))),
                    bad(state_mass_table(transform(d,state=c(0,NA)), 1, c(0,1))),
                    bad(state_mass_table(transform(d,particle=1), 1, c(0,1))),
                    bad(state_mass_table(d, 2, c(0,1))),
                    bad(state_mass_table(d, c(1,1), c(0,1))),
                    bad(state_mass_table(d, 1, c(0,1,1))))
          empty <- state_mass_table(d[FALSE,], 1:3, 0:1)
          stopifnot(all(is.na(empty$cells$mass)), all(empty$summary$n == 0))
        """)

    def test_ggplot_encodes_actual_bin_edges_and_missing_times(self):
        probe = subprocess.run(["Rscript", "--vanilla", "-e",
                                'quit(status=if(requireNamespace("ggplot2",quietly=TRUE)) 0 else 1)'],
                               capture_output=True)
        if probe.returncode:
            self.skipTest("ggplot2 unavailable")
        self.run_r("""
          d <- data.frame(time=c(1,7), state=c(.5,2), weight=c(1,1))
          r <- state_mass_table(d, c(1,3,7), c(0,1,4))
          p <- plot_state_mass(r)
          layers <- ggplot2::ggplot_build(p)$data
          tiles <- layers[[1]]
          stopifnot(inherits(p,"ggplot"), all(tiles$ymin==rep(c(0,1),3)),
                    all(tiles$ymax==rep(c(1,4),3)), all(tiles$xmin==rep(c(0,2,6),each=2)),
                    layers[[2]]$x==3, length(unique(tiles$fill))==3,
                    inherits(try(plot_state_mass(r,mass_max=.5),silent=TRUE),"try-error"))
        """)
