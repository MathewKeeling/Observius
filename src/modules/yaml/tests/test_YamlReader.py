import pytest
import yaml
from typing import Any, Dict, Optional
from src.modules.yaml.YamlReader import YamlReader

yaml_content = """
config:
  server:
    host: localhost
    port: 8080
  credentials:
    - username: admin
      password: secret
"""


def write_yaml_file(file_path: str, content: str):
    with open(file_path, "w") as f:
        f.write(content)


@pytest.fixture
def yaml_file(tmp_path):
    file_path = tmp_path / "config.yaml"
    write_yaml_file(file_path, yaml_content)
    return file_path


def test_load_yaml(yaml_file):
    reader = YamlReader(yaml_file)
    assert reader.data["config"]["server"]["host"] == "localhost"
    assert reader.data["config"]["server"]["port"] == 8080


def test_get_value(yaml_file):
    reader = YamlReader(yaml_file)
    assert reader.get_value("config.server.host") == "localhost"
    assert reader.get_value("config.server.port") == 8080
    assert reader.get_value("config.credentials") == [
        {"username": "admin", "password": "secret"}
    ]
    assert reader.get_value("non.existent.path") is None


def test_get_section(yaml_file):
    reader = YamlReader(yaml_file)
    assert reader.get_section("config.server") == {"host": "localhost", "port": 8080}
    assert reader.get_section("config.credentials") == [
        {"username": "admin", "password": "secret"}
    ]
    assert reader.get_section("non.existent.section") is None


def test_set_value(yaml_file):
    reader = YamlReader(yaml_file)
    reader.set_value("config.server.host", "127.0.0.1")
    assert reader.get_value("config.server.host") == "127.0.0.1"
    reader.set_value("config.new_section.key", "value")
    assert reader.get_value("config.new_section.key") == "value"


def test_delete_value(yaml_file):
    reader = YamlReader(yaml_file)
    reader.delete_value("config.server.host")
    assert reader.get_value("config.server.host") is None
    reader.delete_value("config.credentials")
    assert reader.get_value("config.credentials") is None


def test_save(yaml_file):
    reader = YamlReader(yaml_file)
    reader.set_value("config.server.host", "127.0.0.1")
    reader.save()
    new_reader = YamlReader(yaml_file)
    assert new_reader.get_value("config.server.host") == "127.0.0.1"


def test_reload(yaml_file):
    reader = YamlReader(yaml_file)
    assert reader.data["config"]["server"]["host"] == "localhost"
    new_content = """
    config:
      server:
        host: 127.0.0.1
        port: 9090
    """
    write_yaml_file(yaml_file, new_content)
    reader.reload()
    assert reader.data["config"]["server"]["host"] == "127.0.0.1"
    assert reader.data["config"]["server"]["port"] == 9090


def test_load_yaml_error(tmp_path):
    invalid_yaml_file = tmp_path / "invalid.yaml"
    with open(invalid_yaml_file, "w") as f:
        f.write("invalid: [unbalanced brackets")
    with pytest.raises(Exception, match="Error loading YAML file"):
        YamlReader(invalid_yaml_file)
