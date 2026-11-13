import inspect
import json
from collections.abc import Callable

from functions.get_file_content import get_file_content, schema_get_file_content
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.replace_file_text import replace_file_text, schema_replace_file_text
from functions.run_python_file import run_python_file, schema_run_python_file
from functions.write_file import schema_write_file, write_file

available_functions = [
    schema_get_files_info,
    schema_get_file_content,
    schema_run_python_file,
    schema_write_file,
    schema_replace_file_text,
]


def call_function(
    tool_call, verbose: bool = False, working_directory: str = "./calculator"
) -> dict:
    function_name = tool_call.function.name
    function_map: dict[str, Callable[..., str]] = {
        "get_file_content": get_file_content,
        "get_files_info": get_files_info,
        "run_python_file": run_python_file,
        "write_file": write_file,
        "replace_file_text": replace_file_text,
    }

    def tool_result(content: str) -> dict:
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": content,
        }

    if function_name not in function_map:
        return tool_result(f"Error: Unknown function: {function_name}")

    try:
        function_args = json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError as error:
        return tool_result(f"Error: Invalid function arguments: {error}")
    if not isinstance(function_args, dict):
        return tool_result("Error: Function arguments must be a JSON object")
    if "working_directory" in function_args:
        return tool_result("Error: working_directory is supplied by the agent, not the model")

    schema = next(
        tool["function"]["parameters"]
        for tool in available_functions
        if tool["function"]["name"] == function_name
    )
    for name, value in function_args.items():
        parameter = schema["properties"].get(name)
        if parameter is None:
            return tool_result(f"Error: Unknown argument: {name}")
        if parameter["type"] == "string" and not isinstance(value, str):
            return tool_result(f"Error: {name} must be a string")
        if parameter["type"] == "array" and (
            not isinstance(value, list) or not all(isinstance(item, str) for item in value)
        ):
            return tool_result(f"Error: {name} must be an array of strings")

    if verbose:
        print(f" - Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    # The workspace is selected by the user, never by the model.
    function_args["working_directory"] = working_directory
    try:
        inspect.signature(function_map[function_name]).bind(**function_args)
    except TypeError as error:
        return tool_result(f"Error: Invalid function arguments: {error}")
    return tool_result(function_map[function_name](**function_args))
