import os

from functions.paths import resolve_path


schema_replace_file_text = {
    "type": "function",
    "function": {
        "name": "replace_file_text",
        "description": "Replace one exact occurrence of text in an existing file.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file relative to the working directory.",
                },
                "old_text": {
                    "type": "string",
                    "description": "Exact existing text to replace; it must occur once.",
                },
                "new_text": {
                    "type": "string",
                    "description": "Text to insert in its place.",
                },
            },
            "required": ["file_path", "old_text", "new_text"],
        },
    },
}


def replace_file_text(
    working_directory: str, file_path: str, old_text: str, new_text: str
) -> str:
    if not old_text:
        return "Error: old_text must not be empty"
    try:
        try:
            target = resolve_path(working_directory, file_path)
        except ValueError:
            return f'Error: Cannot edit "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        with open(target, "r", encoding="utf-8", newline="") as file:
            content = file.read()
        position = content.find(old_text)
        if position == -1 or content.find(old_text, position + 1) != -1:
            return "Error: old_text must match exactly once; no changes were made"
        updated = content[:position] + new_text + content[position + len(old_text):]
        updated.encode("utf-8")
        with open(target, "w", encoding="utf-8", newline="") as file:
            file.write(updated)
        return f'Successfully edited "{file_path}"'
    except (OSError, UnicodeError) as error:
        return f"Error: {error}"
