from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'assets/r-template/R/plot_sample_atlas.R'


class SampleAtlasTest(unittest.TestCase):
    def test_keyed_matrix_numeric_encoding_and_input_failures(self):
        r = shutil.which('Rscript')
        if not r:
            self.skipTest('Rscript unavailable')
        probe = subprocess.run([r, '--vanilla', '-e',
                                'quit(status = as.integer(!requireNamespace("ggplot2", quietly=TRUE)))'])
        if probe.returncode:
            self.skipTest('ggplot2 unavailable')
        script = r"""
          source(commandArgs(trailingOnly=TRUE)[1])
          s <- data.frame(id=c('c', 'a', 'b'), x=c(0, -2, NA_real_), y=c(3, 4, 7))
          meta <- data.frame(id=c('a', 'b', 'c'), group=c('G1', 'G2', 'G1'))
          draw <- function(meta=meta_input, order=c('b','c','a'), reps='c', limits=NULL) {
            plot_sample_atlas(s, meta, c('y','x'), c(G1='#C289A0',G2='#527F94'),
                              'Feature z-score', id='id', sample_order=order,
                              medoid_ids=reps, midpoint=0, limits=limits)
          }
          meta_input <- meta
          p <- draw()
          d <- p$data
          stopifnot(inherits(p, 'ggplot'), nrow(d)==6, identical(d$value, c(7,3,4,NA,0,-2)),
                    identical(d$sample_id, rep(c('b','c','a'),2)),
                    identical(d$group, rep(c('G2','G1','G1'),2)),
                    identical(d$row_index,c(2L,2L,2L,1L,1L,1L)),
                    identical(d$is_medoid, rep(c(FALSE,TRUE,FALSE),2)))
          built <- ggplot2::ggplot_build(p)
          layers <- built$data
          stopifnot(toupper(layers[[1]]$fill[4])=='#B9B9B9',
                    toupper(layers[[1]]$fill[5])=='#FAF7F5',
                    nrow(layers[[3]])==1L, layers[[3]]$x==1, layers[[3]]$y==1,
                    nrow(layers[[4]])==1L, layers[[4]]$x==2,
                    layers[[4]]$y < max(built$layout$panel_params[[1]]$y.range))
          fails <- function(expr) inherits(try(expr, silent=TRUE), 'try-error')
          stopifnot(fails(draw(meta=meta[c(1,1,3),])),
                    fails(draw(meta=meta[-1,])), fails(draw(order=c('b','c'))),
                    fails(draw(reps='centroid-1')), fails(draw(reps=c(G2='c'))),
                    inherits(draw(reps=c(G1='c')), 'ggplot'), fails(draw(limits=c(-1,8))))
          print(p)
        """
        with tempfile.TemporaryDirectory(prefix='atlas check ') as tmp:
            run = subprocess.run([r, '--vanilla', '-e', script, str(TEMPLATE)], cwd=tmp,
                                 text=True, capture_output=True, timeout=60)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertGreater((Path(tmp) / 'Rplots.pdf').stat().st_size, 1000)
