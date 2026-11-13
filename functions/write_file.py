import os

from functions.paths import resolve_path

schema_write_file = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write content to a file in the working directory",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The relative path to the file to write to, relative to the working directory",
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file",
                },
            },
            "required": [ "file_path", "content"],
        },
    }
}

def write_file(working_directory: str, file_path: str, content: str) -> str:
    try:
        content.encode("utf-8")
        try:
            target_path = resolve_path(working_directory, file_path)
        except ValueError:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        if os.path.isdir(target_path):
            return f'Error: Cannot write to "{file_path}" as it is a directory'

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )
    except (OSError, UnicodeError) as e:
        return f"Error: {e}"
