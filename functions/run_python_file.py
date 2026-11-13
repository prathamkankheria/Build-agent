import os
import subprocess
import sys

from functions.paths import resolve_path

schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Run a Python file and return the output.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to a Python file relative to the working directory.",
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional command-line arguments for the Python file.",
                },
            },
            "required": ["file_path"],
        },
    },
}


def run_python_file(
        working_directory: str, file_path: str, args: list[str] | None = None
    ) -> str:
    try:
        working_directory_absolute = os.path.realpath(working_directory)
        try:
            target_file_path = resolve_path(working_directory, file_path)
        except ValueError:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not target_file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = [sys.executable, target_file_path]
        if args:
            command.extend(args)
        result = subprocess.run(
            command,
            cwd=working_directory_absolute,
            capture_output=True,
            text=True,
            check=False,
            timeout=30
        )
        output_string = ""
        if result.returncode != 0:
            output_string += f"\nProcess exited with code {result.returncode}\n"
        if not result.stderr and not result.stdout:
            output_string += "No output was produced"
        if result.stderr:
            output_string += f"\nSTDERR:\n{result.stderr}"
        if result.stdout:
            output_string += f"\nSTDOUT:\n{result.stdout}"
        return output_string

    except subprocess.TimeoutExpired:
        return f'Error: executing "{file_path}" timed out after 30 seconds'
    except OSError as e:
        return f"Error: executing Python file: {e}"
