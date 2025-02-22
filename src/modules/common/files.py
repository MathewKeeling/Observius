import pandas as pd


def csv_to_dict(file_path: str) -> list:
    """Converts a CSV file to a list of dictionaries.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of dictionaries.
    """
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return []
        return df.to_dict(orient="records")
    except pd.errors.EmptyDataError:
        return []
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        raise


def search_dict_list(dict_list: list, key: str, value: str) -> dict:
    """Searches a list of dictionaries for a key-value pair

    Args:
        dict_list (list): A list of dictionaries.
        key (str): The key to search for.
        value (str): The value to search for.

    Returns:
        dict: The dictionary that contains the key-value pair.

    """
    for dictionary in dict_list:
        if dictionary.get(key) == value:
            return dictionary
    return None


def file_to_string(file_path) -> str:
    """Converts a file to a string.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The contents of the file as a string.
    """
    with open(file_path, "r") as file:
        return file.read()


def string_to_file(file_path: str, string: str) -> None:
    """
    Export a string to a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        None
    """
    with open(file_path, "w") as f:
        f.write(string)


if __name__ == "__main__":
    print(csv_to_dict(".secrets/credentials.csv"))
