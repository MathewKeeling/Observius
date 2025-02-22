import yaml
from typing import Any, Dict, Optional


class YamlReader:
    def __init__(self, yaml_file: str):
        self.yaml_file = yaml_file
        self.data = self._load_yaml()

    def _load_yaml(self) -> Dict:
        try:
            with open(self.yaml_file, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Error loading YAML file: {str(e)}")

    def get_value(self, path: str) -> Any:
        current = self.data
        for key in path.split("."):
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return None
        return current

    def get_section(self, path: str) -> Optional[Dict]:
        return self.get_value(path)

    def set_value(self, path: str, value: Any):
        keys = path.split(".")
        current = self.data
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def delete_value(self, path: str):
        keys = path.split(".")
        current = self.data
        for key in keys[:-1]:
            if key in current and isinstance(current[key], dict):
                current = current[key]
            else:
                return
        current.pop(keys[-1], None)

    def save(self):
        try:
            with open(self.yaml_file, "w") as f:
                yaml.safe_dump(self.data, f)
        except Exception as e:
            raise Exception(f"Error saving YAML file: {str(e)}")

    def reload(self):
        self.data = self._load_yaml()
