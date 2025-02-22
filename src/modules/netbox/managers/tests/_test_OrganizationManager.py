from src.modules.netbox.NetBoxAPI import NetBoxAPI
from src.modules.yaml.YamlReader import YamlReader
import logging
import requests

if __name__ == "__main__":
    secrets_path = "resources/etc/secrets/secrets.yaml"
    netbox_api_yaml_path = "resources/etc/connectors/netbox/netbox_api.yaml"
    roles_yaml_path = "resources/etc/connectors/netbox/config/roles.yaml"
    secrets = YamlReader(yaml_file=secrets_path)
    netbox_api_config = YamlReader(yaml_file=netbox_api_yaml_path)

    base_url = netbox_api_config.get_value(path="netbox_api.base_url")
    api_token = secrets.get_value(path="secrets.netbox_api_token.api_token")

    logging.debug(f"API Token: {api_token}")

    netbox_api = NetBoxAPI(api_token=api_token, base_url=base_url)

    organizations = netbox_api.organization_manager.get_organizations()
    for organization in organizations["results"]:
        print(organization)
