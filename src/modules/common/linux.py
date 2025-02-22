import os
from typing import Optional


def create_dir(directory: str) -> None:
    """Creates a directory if it does not exist.

    Args:
        directory (str): The path of the directory to create.

    Returns:
        None
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError as e:
        print(f"Error creating directory {directory}: {e}")
        raise


def get_all_file_paths(directory):
    """
    Recursively get all file paths in the given directory.

    :param directory: The directory to search for files.
    :return: A list of file paths.
    """
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths


def path_minus_file(path: str) -> Optional[str]:
    """Returns the directory path without the file name.

    Args:
        path (str): The full path including the file name.

    Returns:
        Optional[str]: The directory path without the file name, or None if the path is invalid.
    """
    if not path:
        return None
    return os.path.dirname(path)
