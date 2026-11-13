import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import main
from call_function import call_function
from config import MAX_CHARS
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.replace_file_text import replace_file_text
from functions.run_python_file import run_python_file
from functions.write_file import write_file


def tool_call(name, arguments, call_id="call-1"):
    return SimpleNamespace(
        id=call_id,
        type="function",
        function=SimpleNamespace(name=name, arguments=arguments),
    )


class AgentToolsTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_read_truncation_and_edit_exact_match(self):
        path = self.root / "example.txt"
        path.write_text("x" * (MAX_CHARS + 1), encoding="utf-8")
        self.assertIn("truncated", get_file_content(str(self.root), path.name))
        path.write_text("before\r\nmiddle\r\nafter\r\n", encoding="utf-8", newline="")
        self.assertIn("Successfully", replace_file_text(
            str(self.root), path.name, "middle", "changed"
        ))
        self.assertEqual(path.read_bytes(), b"before\r\nchanged\r\nafter\r\n")
        self.assertIn("Error", replace_file_text(str(self.root), path.name, "e", "x"))
        self.assertEqual(path.read_bytes(), b"before\r\nchanged\r\nafter\r\n")
        path.write_text("aaa", encoding="utf-8")
        self.assertIn("Error", replace_file_text(str(self.root), path.name, "aa", "x"))
        self.assertEqual(path.read_text(encoding="utf-8"), "aaa")

    def test_paths_reject_symlinks_outside_workspace(self):
        with tempfile.TemporaryDirectory() as external:
            outside = Path(external) / "outside.txt"
            outside.write_text("safe", encoding="utf-8")
            (self.root / "link").symlink_to(outside)
            (self.root / "external").symlink_to(external, target_is_directory=True)
            self.assertIn("Error", get_file_content(str(self.root), "link"))
            self.assertIn("Error", write_file(str(self.root), "link", "changed"))
            self.assertIn("Error", replace_file_text(str(self.root), "link", "safe", "changed"))
            self.assertIn("Error", get_files_info(str(self.root), "external"))
            self.assertIn("Error", run_python_file(str(self.root), "external/a.py"))
            self.assertEqual(outside.read_text(encoding="utf-8"), "safe")

    def test_python_runs_in_workspace_with_current_interpreter(self):
        script = self.root / "script.py"
        script.write_text(
            "import os, sys\nprint(os.getcwd())\nprint(sys.argv[1])\n",
            encoding="utf-8",
        )
        result = run_python_file(str(self.root), "script.py", ["argument"])
        self.assertEqual(result.count("argument"), 1)
        self.assertIn(str(self.root), result)
        with patch(
            "functions.run_python_file.subprocess.run",
            side_effect=subprocess.TimeoutExpired("python", 30),
        ):
            self.assertIn("timed out", run_python_file(str(self.root), "script.py"))

    def test_dispatch_validates_arguments_and_injects_workspace(self):
        with contextlib.redirect_stdout(io.StringIO()):
            result = call_function(
                tool_call("write_file", json.dumps({"file_path": "new.txt", "content": "hello"})),
                working_directory=str(self.root),
            )
        self.assertIn("Successfully", result["content"])
        self.assertEqual((self.root / "new.txt").read_text(), "hello")
        for arguments in ('{', '[]', '{"working_directory": "/tmp"}', '{"file_path": 3}'):
            result = call_function(tool_call("get_file_content", arguments))
            self.assertTrue(result["content"].startswith("Error:"))
        result = call_function(tool_call("unknown", "{}"))
        self.assertIn("Unknown function", result["content"])

    def test_main_feeds_tool_result_back_to_model(self):
        (self.root / "file.txt").write_text("contents", encoding="utf-8")
        first_message = SimpleNamespace(
            content=None,
            tool_calls=[tool_call("get_file_content", '{"file_path": "file.txt"}')],
        )
        final_message = SimpleNamespace(content="Done", tool_calls=None)
        seen = []

        def create(**kwargs):
            seen.append(list(kwargs["messages"]))
            message = first_message if len(seen) == 1 else final_message
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        with patch.object(main, "OpenAI", return_value=client), \
             patch("sys.argv", ["main.py", "--working-directory", str(self.root), "read"]), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            main.main("test-key")
        self.assertEqual(seen[1][-1]["content"], "contents")
        self.assertIn("Done", output.getvalue())

    def test_main_reports_iteration_limit(self):
        message = SimpleNamespace(
            content=None,
            tool_calls=[tool_call("get_file_content", '{"file_path": "missing"}')],
        )
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
            create=lambda **kwargs: SimpleNamespace(choices=[SimpleNamespace(message=message)])
        )))
        with patch.object(main, "OpenAI", return_value=client), \
             patch("sys.argv", ["main.py", "--working-directory", str(self.root), "read"]), \
             contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "Maximum iterations"):
                main.main("test-key")


if __name__ == "__main__":
    unittest.main()
