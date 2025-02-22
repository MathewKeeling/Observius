import json
from typing import Any


def json_to_file(obj: Any, file_path: str) -> None:
    """Writes a Python object to a JSON file.

    Args:
        obj (Any): The Python object to write to the file.
        file_path (str): The path to the JSON file.

    Returns:
        None
    """
    try:
        with open(file_path, "w") as json_file:
            json.dump(obj, json_file, indent=4)
    except (TypeError, ValueError) as e:
        print(f"Error writing to JSON file: {e}")
        raise


def file_to_json(file_path: str) -> Any:
    """Reads a JSON file and returns the corresponding Python object.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        Any: The Python object represented by the JSON file.
    """
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        raise


def pretty_print_json(obj: Any) -> str:
    """Returns a pretty-printed JSON string of a Python object.

    Args:
        obj (Any): The Python object to convert to a pretty-printed JSON string.

    Returns:
        str: The pretty-printed JSON string.
    """
    try:
        return json.dumps(obj, indent=4)
    except (TypeError, ValueError) as e:
        print(f"Error converting to pretty-printed JSON: {e}")
        raise
