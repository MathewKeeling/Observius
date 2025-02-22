from src.modules.netbox.NetBoxAPI import NetBoxAPI
from src.modules.yaml.YamlReader import YamlReader
import logging

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

    ip_addresses_yaml_path = "resources/etc/connectors/netbox/config/ip_addresses.yaml"
    ip_addresses_yaml = YamlReader(yaml_file=ip_addresses_yaml_path)
    ipam_info = ip_addresses_yaml.get_section("ip_addresses")

    # Creating IPv4 Address Test
    # for ipv4_range in ipam_info['ipv4_ranges']:
    #     logging.info(f"Creating IPv4 Range: {ipv4_range}")
    #     netbox_api.ipam_manager.create_ipv4_range(base_address=ipv4_range['base_address'], subnet_mask=ipv4_range['subnet_mask'])

    # Get IPv4 Addresses Test
    # ipv4_addresses = netbox_api.ipam_manager.get_ipv4_addresses()
    # ipv4_specific_id = netbox_api.ipam_manager.get_netbox_id(ip_address="127.0.0.1", subnet_mask=32)

    # print("IPv4 Addresses:")
    # print(ipv4_addresses)
    # print("Specific IPv4 ID:")
    # print(ipv4_specific_id)

    # Creating IPv4 Address Test
    # netbox_api.ipam_manager.load_yaml_and_create_ips()

    # Creating IP Range Test
    # netbox_api.ipam_manager.load_yaml_and_create_ip_ranges()

    # Deleting IPv4 Address Test
    netbox_api.ipam_manager.delete_ipv4(ip_address="127.0.0.1", subnet_mask=32)
