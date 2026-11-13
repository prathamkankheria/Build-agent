import os

from config import MAX_CHARS
from functions.paths import resolve_path

schema_get_file_content = {
    "type": "function",
    "function": {
        "name": "get_file_content",
        "description": "Reads the content of a file in the working directory and returns it as a string. If the file is too large, it will be truncated to the first MAX_CHARS characters.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The relative path to the file from the working directory.",
                },
            },
            "required": ["file_path"],
        },
    }
}


def get_file_content(working_directory: str, file_path: str) -> str:
    try:
        try:
            target_file_path = resolve_path(working_directory, file_path)
        except ValueError:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(target_file_path, "r", encoding="utf-8") as f:
            file_content_string = f.read(MAX_CHARS + 1)
            if len(file_content_string) > MAX_CHARS:
                file_content_string = file_content_string[:MAX_CHARS]
                file_content_string += (
                    f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
                )
        return file_content_string
    except (OSError, UnicodeError) as e:
        return f"Error: {e}"
