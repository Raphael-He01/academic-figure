import argparse
import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/scaffold_project.py"
spec = importlib.util.spec_from_file_location("scaffold_project", SCRIPT)
scaffold = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scaffold)


class ScaffoldTransactionTest(unittest.TestCase):
    def run_scaffold(self, project):
        with mock.patch.object(scaffold, "parse_args", return_value=argparse.Namespace(destination=project)):
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                return scaffold.main()

    def test_file_in_place_of_directory_is_found_before_copying(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            blocker = project / "scripts"
            blocker.write_text("my script", encoding="utf-8")
            with mock.patch.object(scaffold.shutil, "copyfileobj") as copy:
                self.assertEqual(self.run_scaffold(project), 3)
                copy.assert_not_called()
            self.assertEqual(list(project.iterdir()), [blocker])

    def test_interrupted_copy_removes_partial_output_and_new_parent_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "new" / "project"
            def interrupt(reader, writer):
                writer.write(b"partial")
                raise OSError("simulated write failure")
            with mock.patch.object(scaffold.shutil, "copyfileobj", side_effect=interrupt):
                self.assertEqual(self.run_scaffold(project), 2)
            self.assertEqual(list(Path(temp).iterdir()), [])
            self.assertEqual(self.run_scaffold(project), 0)

    def test_late_target_is_preserved_and_own_files_are_rolled_back(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            target = project / "scripts/check_r_project.R"
            original_copy = scaffold.shutil.copyfileobj
            def add_late_target(reader, writer):
                if not target.exists():
                    target.parent.mkdir(exist_ok=True)
                    target.write_text("user content", encoding="utf-8")
                original_copy(reader, writer)
            with mock.patch.object(scaffold.shutil, "copyfileobj", side_effect=add_late_target):
                self.assertEqual(self.run_scaffold(project), 3)
            self.assertEqual(target.read_text(encoding="utf-8"), "user content")
            self.assertEqual(set(project.rglob("*")), {target.parent, target})

    def test_simultaneous_creators_leave_one_complete_project(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "shared"
            command = [sys.executable, "-B", str(SCRIPT), str(project)]
            output = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
            with subprocess.Popen(command, **output) as first, subprocess.Popen(command, **output) as second:
                codes = sorted(process.wait(timeout=30) for process in (first, second))
            self.assertEqual(codes, [0, 3])
            expected = {path.relative_to(SCRIPT.parents[1] / "assets/r-template")
                        for path in (SCRIPT.parents[1] / "assets/r-template").rglob("*") if path.is_file()}
            expected.update({Path("data/palettes/catalog.json"), Path("scripts/check_r_project.R")})
            self.assertEqual({path.relative_to(project) for path in project.rglob("*") if path.is_file()}, expected)
