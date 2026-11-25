import argparse
import contextlib
import importlib.util
import io
from pathlib import Path
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
                    target.write_text("user content", encoding="utf-8")
                original_copy(reader, writer)
            with mock.patch.object(scaffold.shutil, "copyfileobj", side_effect=add_late_target):
                self.assertEqual(self.run_scaffold(project), 3)
            self.assertEqual(target.read_text(encoding="utf-8"), "user content")
            self.assertEqual(set(project.rglob("*")), {target.parent, target})
