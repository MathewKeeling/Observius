from src.modules.common.files import csv_to_dict
from src.modules.yaml.YamlReader import YamlReader
import hvac
import os


def get_secrets_from_file(file_path: str) -> dict:
    """Get secrets from file"""
    return csv_to_dict(file_path)


def get_secrets_from_yaml(file_path: str) -> dict:
    """Get secrets from YAML file"""
    yaml_reader = YamlReader(yaml_file=file_path)
    return yaml_reader.data


def get_secrets_from_vault(vault_path, vault_key):
    """Get secrets from Vault"""
    vault = hvac.Client(url=os.environ["VAULT_ADDR"], token=os.environ["VAULT_TOKEN"])
    secret = vault.read(vault_path)
    return secret["data"][vault_key]


if __name__ == "__main__":
    print("This file is running directly.")
