"""First-use checks must preserve routes and repair the library actually used."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts/check_environment.py"
RCHECK = ROOT / "scripts/check_r_project.R"
spec = importlib.util.spec_from_file_location("figure_environment", CHECK)
env_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(env_check)


class FirstRun(unittest.TestCase):
    def test_missing_r_and_studio_produce_actionable_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "uninstalled")
            result = subprocess.run([sys.executable, str(CHECK), "--route", "rstudio",
                                     "--json", "--rscript", missing, "--rstudio", missing],
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 2)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "needs_setup")
            self.assertIsNone(report["Rscript"])
            self.assertTrue(any("cran.r-project.org" in s for s in report["setup_actions"]))
            self.assertTrue(any("posit.co" in s for s in report["setup_actions"]))

    def test_redirected_windows_codepage_returns_utf8_compatible_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "uninstalled")
            result = subprocess.run([sys.executable, str(CHECK), "--route", "rstudio", "--json",
                                     "--rscript", missing, "--rstudio", missing],
                                    env=dict(os.environ, PYTHONIOENCODING="cp1252"), capture_output=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertTrue(result.stdout.isascii())
        report = json.loads(result.stdout.decode("utf-8"))
        self.assertEqual(report["status"], "needs_setup")
        self.assertIn("安装", report["setup_actions"][0])

    def test_origin_and_palette_skip_r_completely(self):
        with patch.object(env_check, "probe_r", side_effect=AssertionError("Unexpected R probe")):
            self.assertEqual(env_check.inspect_route("palette")["status"], "ready")
            with patch.object(env_check.platform, "system", return_value="Darwin"):
                report = env_check.inspect_route("origin")
                self.assertEqual(report["status"], "needs_setup")
                self.assertTrue(any("Windows" in s for s in report["setup_actions"]))

    def test_no_r_inventory_remains_reportable(self):
        with patch.object(env_check, "find_program", return_value=None):
            with patch.object(sys, "argv", [str(CHECK), "--json"]):
                with patch("builtins.print"):
                    self.assertEqual(env_check.main(), 0)


    def test_authorized_system_installer_resumes_and_retries_only_missing_apps(self):
        installed = {}
        attempted = []
        def lookup(name, override, system):
            return installed.get(name)
        def manager(command, **kwargs):
            cask = command[-1]
            attempted.append(cask)
            if cask == "rstudio" and attempted.count(cask) == 1:
                return subprocess.CompletedProcess(command, 9)
            program = "Rscript" if cask == "r-app" else "rstudio"
            installed[program] = "/isolated/" + program
            return subprocess.CompletedProcess(command, 0)
        def invoke(with_install):
            argv = [str(CHECK), "--route", "rstudio"]
            if with_install:
                argv.append("--install-missing")
            with patch.object(sys, "argv", argv), patch("builtins.print") as output:
                code = env_check.main()
            return code, json.loads(output.call_args.args[0])
        with patch.object(env_check.platform, "system", return_value="Darwin"), \
             patch.object(env_check, "find_program", side_effect=lookup), \
             patch.object(env_check.shutil, "which", side_effect=lambda name: name if name == "brew" else None), \
             patch.object(env_check, "probe_r", return_value={"r_probe_exit": 0}), \
             patch.object(env_check.subprocess, "run", side_effect=manager):
            self.assertEqual(invoke(False)[0], 2)
            self.assertEqual(attempted, [])
            code, report = invoke(True)
            self.assertEqual(code, 2)
            self.assertEqual(report["install_attempts"][-1]["exit"], 9)
            self.assertIsNotNone(report["Rscript"])
            code, report = invoke(True)
            self.assertEqual(code, 0)
            self.assertEqual(report["status"], "check_project_session")
            self.assertEqual(attempted, ["r-app", "rstudio", "rstudio"])
            self.assertEqual(invoke(True)[1]["install_attempts"], [])

    def test_linux_repository_and_privilege_handoff(self):
        report = {"platform": "Linux", "route": "rscript", "Rscript": None}
        with patch.object(env_check.shutil, "which",
                          side_effect=lambda name: name if name in ("apt-get", "apt-cache") else None), \
             patch.object(env_check.os, "geteuid", return_value=1000, create=True), \
             patch.object(env_check.subprocess, "run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, " Candidate: 4.5.1\n")
            needed = env_check.install_missing(report, {})[0]
            self.assertIn("sudo apt-get install", needed["action"])
            self.assertEqual(run.call_count, 1)
            run.return_value = subprocess.CompletedProcess([], 0, " Candidate: (none)\n")
            self.assertIn("cran.r-project.org", env_check.install_missing(report, {})[0]["action"])
            self.assertTrue(all(call.args[0][0] == "apt-cache" for call in run.call_args_list))

    @unittest.skipUnless(shutil.which("Rscript"), "Rscript unavailable")
    def test_install_in_isolated_user_library_and_resume_in_new_session(self):
        # Build a local CRAN-style source repository without using the network.
        with tempfile.TemporaryDirectory(prefix="figure first run ") as temp:
            work = Path(temp)
            package = work / "figureSetupFixture"
            package.mkdir()
            (package / "DESCRIPTION").write_text(
                "Package: figureSetupFixture\nVersion: 0.0.1\nTitle: Setup Fixture\n"
                "Description: Local package for setup tests.\n"
                "Author: Test Author\nMaintainer: Test Author <test@example.org>\n"
                "License: MIT\n", encoding="utf-8")
            (package / "NAMESPACE").write_text("exportPattern(\"^[[:alpha:]]+\")\n", encoding="utf-8")
            (package / "R").mkdir()
            (package / "R/figure.R").write_text("answer <- function() 42L\n", encoding="utf-8")
            repo = work / "repo/src/contrib"
            repo.mkdir(parents=True)
            settings = dict(os.environ, R_LIBS_USER=str(work / "user-library"), RENV_PROJECT="",
                            FIXTURE_REPO=unquote((work / "repo").as_uri()), FIGURE_SETUP_SCRIPT=str(RCHECK))
            make_repo = """
                binary <- file.path(R.home("bin"), "R")
                args <- c("CMD", "build", "--no-build-vignettes", "--no-manual",
                          shQuote(commandArgs(TRUE)[1]))
                stopifnot(system2(binary, args) == 0L)
                tools::write_PACKAGES(".", type="source")
            """
            def run_r(code, cwd, *args):
                result = subprocess.run([shutil.which("Rscript"), "--vanilla", "-e", code, *args],
                                        env=settings, cwd=cwd, capture_output=True, text=True,
                                        encoding="utf-8", errors="replace", timeout=120)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            run_r(make_repo, repo, str(package))
            install = """
                source(Sys.getenv("FIGURE_SETUP_SCRIPT"))
                options(pkgType="source")
                needs <- c("figureSetupFixture (>= 0.0.1)")
                stopifnot(!check_figure_environment(needs)$ready)
                stopifnot(!dir.exists(Sys.getenv("R_LIBS_USER")))
                result <- check_figure_environment(needs, install=TRUE,
                                                   repos=Sys.getenv("FIXTURE_REPO"))
                stopifnot(result$ready, figureSetupFixture::answer() == 42L)
                stopifnot(normalizePath(find.package("figureSetupFixture")) ==
                          normalizePath(file.path(Sys.getenv("R_LIBS_USER"), "figureSetupFixture")))
            """
            run_r(install, work)
            run_r("""
                source(Sys.getenv("FIGURE_SETUP_SCRIPT"))
                stopifnot(check_figure_environment("figureSetupFixture")$ready)
                stopifnot(!check_figure_environment("figureSetupFixture (>= 1.0)")$ready)
                grDevices::pdf("resumed-figure.pdf")
                graphics::plot(figureSetupFixture::answer())
                grDevices::dev.off()
            """, work)
            self.assertGreater((work / "resumed-figure.pdf").stat().st_size, 100)

            # An unopened renv project must not accidentally install into a global library.
            (work / ".Rprofile").write_text('source("renv/activate.R")\n', encoding="utf-8")
            run_r("""
                source(Sys.getenv("FIGURE_SETUP_SCRIPT"))
                stopifnot(inherits(try(check_figure_environment("stats", install=TRUE),
                                       silent=TRUE), "try-error"))
            """, work)
