import pytest
import os
from src.modules.common.linux import create_dir, path_minus_file


def test_create_dir(tmp_path):
    dir_path = tmp_path / "new_dir"
    create_dir(dir_path)
    assert os.path.exists(dir_path)


def test_create_dir_existing(tmp_path):
    dir_path = tmp_path / "existing_dir"
    os.makedirs(dir_path)
    create_dir(dir_path)  # Should not raise an error
    assert os.path.exists(dir_path)


def test_create_dir_invalid_path():
    with pytest.raises(OSError):
        create_dir("/invalid_path/new_dir")


def test_path_minus_file():
    path = "/home/user/file.txt"
    expected = "/home/user"
    result = path_minus_file(path)
    assert result == expected


def test_path_minus_file_no_file():
    path = "/home/user/"
    expected = "/home/user"
    result = path_minus_file(path)
    assert result == expected


def test_path_minus_file_empty():
    path = ""
    result = path_minus_file(path)
    assert result is None


def test_path_minus_file_none():
    path = None
    result = path_minus_file(path)
    assert result is None
