import os


def resolve_path(working_directory: str, path: str) -> str:
    # Resolve symlinks before checking containment, including for new files.
    root = os.path.realpath(working_directory)
    target = os.path.realpath(os.path.join(root, path))
    if os.path.commonpath([root, target]) != root:
        raise ValueError(f'Path "{path}" is outside the permitted working directory')
    return target
