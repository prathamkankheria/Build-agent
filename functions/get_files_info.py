import os

from functions.paths import resolve_path

schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list files from, relative to the working directory (default is the working directory itself)",
                },
            },
        },
    },
}

def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        try:
            target_dir = resolve_path(working_directory, directory)
        except ValueError:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        list_of_dir = sorted(os.listdir(target_dir))

        def get_meta_data(filename: str) -> str:
            path_of_item = os.path.join(target_dir, filename)
            if os.path.islink(path_of_item):
                return f" - {filename}: is_symlink=True"
            item_size = os.path.getsize(path_of_item)
            is_dir = os.path.isdir(path_of_item)

            return f" - {filename}: file_size={item_size} bytes, is_dir={is_dir}"

        info_of_list = map(get_meta_data, list_of_dir)
        first_line = f"Result for {"current" if directory == "." else directory} directory:\n"
        return first_line + "\n".join(info_of_list)
    except OSError as e:
        return f"Error: {e}"
