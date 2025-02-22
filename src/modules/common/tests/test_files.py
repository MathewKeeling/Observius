import pytest
import pandas as pd
from src.modules.common.files import (
    csv_to_dict,
    search_dict_list,
    file_to_string,
    string_to_file,
)


@pytest.fixture
def sample_csv(tmp_path):
    data = "name,age\nAlice,30\nBob,25"
    file_path = tmp_path / "sample.csv"
    file_path.write_text(data)
    return file_path


@pytest.fixture
def empty_csv(tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("")
    return file_path


@pytest.fixture
def malformed_csv(tmp_path):
    data = "name,age\nAlice,30\nBob"
    file_path = tmp_path / "malformed.csv"
    file_path.write_text(data)
    return file_path


@pytest.fixture
def sample_dict_list():
    return [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]


@pytest.fixture
def empty_dict_list():
    return []


def test_csv_to_dict(sample_csv):
    expected = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    result = csv_to_dict(sample_csv)
    assert result == expected


def test_csv_to_dict_empty(empty_csv):
    result = csv_to_dict(empty_csv)
    assert result == []


def test_csv_to_dict_malformed(malformed_csv):
    try:
        csv_to_dict(malformed_csv)
    except Exception as e:
        print(f"Raised exception: {e}")
        raise


def test_search_dict_list_found(sample_dict_list):
    result = search_dict_list(sample_dict_list, "name", "Alice")
    expected = {"name": "Alice", "age": 30}
    assert result == expected


def test_search_dict_list_not_found(sample_dict_list):
    result = search_dict_list(sample_dict_list, "name", "Charlie")
    assert result is None


def test_search_dict_list_empty(empty_dict_list):
    result = search_dict_list(empty_dict_list, "name", "Alice")
    assert result is None


def test_file_to_string(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Hello, World!")
    result = file_to_string(file_path)
    assert result == "Hello, World!"


def test_file_to_string_empty(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("")
    result = file_to_string(file_path)
    assert result == ""


def test_file_to_string_nonexistent(tmp_path):
    file_path = tmp_path / "nonexistent.txt"
    with pytest.raises(FileNotFoundError):
        file_to_string(file_path)


def test_string_to_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    string_to_file(file_path, "Hello, World!")
    result = file_path.read_text()
    assert result == "Hello, World!"


def test_string_to_file_overwrite(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Old Content")
    string_to_file(file_path, "New Content")
    result = file_path.read_text()
    assert result == "New Content"
