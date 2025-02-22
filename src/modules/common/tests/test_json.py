import pytest
import json
from src.modules.common.json import json_to_file, file_to_json, pretty_print_json


@pytest.fixture
def sample_json(tmp_path):
    data = {"name": "Alice", "age": 30}
    file_path = tmp_path / "sample.json"
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    return file_path


def test_json_to_file(tmp_path):
    data = {"name": "Alice", "age": 30}
    file_path = tmp_path / "output.json"
    json_to_file(data, file_path)
    with open(file_path, "r") as json_file:
        result = json.load(json_file)
    assert result == data


def test_json_to_file_invalid_type(tmp_path):
    data = {"name": "Alice", "age": set([30])}  # Sets are not JSON serializable
    file_path = tmp_path / "output.json"
    with pytest.raises(TypeError):
        json_to_file(data, file_path)


def test_file_to_json(sample_json):
    expected = {"name": "Alice", "age": 30}
    result = file_to_json(sample_json)
    assert result == expected


def test_file_to_json_nonexistent(tmp_path):
    file_path = tmp_path / "nonexistent.json"
    with pytest.raises(FileNotFoundError):
        file_to_json(file_path)


def test_file_to_json_invalid_json(tmp_path):
    file_path = tmp_path / "invalid.json"
    file_path.write_text("{name: Alice, age: 30}")  # Invalid JSON format
    with pytest.raises(json.JSONDecodeError):
        file_to_json(file_path)


def test_pretty_print_json():
    data = {"name": "Alice", "age": 30}
    expected = json.dumps(data, indent=4)
    result = pretty_print_json(data)
    assert result == expected


def test_pretty_print_json_invalid_type():
    data = {"name": "Alice", "age": set([30])}  # Sets are not JSON serializable
    with pytest.raises(TypeError):
        pretty_print_json(data)
