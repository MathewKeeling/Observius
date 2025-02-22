from src.modules.netbox.NetBoxAPI import NetBoxAPI
from src.modules.netbox.managers.DeviceManager import DeviceManager
from src.modules.yaml.YamlReader import YamlReader
from src.modules.device.Device import (
    Device,
    convert_df_to_devices,
)
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

    # Example usage
    device_manager = DeviceManager(netbox_api)

    # Create device from YAML
    # manager.create_device_from_yaml(netbox_api_yaml_path)

    # Create device from DataFrame
    device_instance = Device(
        categories=["Router"],
        dns_name="a.test.com",
        first_seen=1617181920,
        foreignId="12345",
        foreignSource="Network",
        # ipv4="127.0.0.1",
        labelSource="Manual",
        last_seen=1617181930,
        location="Office",
        mac="00:1A:2B:3C:4D:5E",
        type="Router",
        id="device123",  # Add a unique identifier for the device
    )
    df = device_instance.device_to_netbox_dataframe()
    # add device_type and device_role to the dataframe3
    df["status"] = "active"
    df["site"] = "1"
    df["device_type"] = 41
    df["role"] = 73
    # df["primary_ip4"] = 555
    print(df)
    device_manager.create_device_from_dataframe(df)
