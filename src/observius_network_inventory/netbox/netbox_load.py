from src.modules.common.LoggerSetup import LoggerSetup
from src.modules.yaml.YamlReader import YamlReader
from src.modules.common.linux import create_dir, path_minus_file
from src.modules.netbox.NetBoxAPI import NetBoxAPI
from src.modules.sqlite.main import SQLiteManager
from src.modules.device.Device import (
    Device,
    convert_df_to_devices,
    purge_empty_values_from_dataframe,
)
import os


def main():
    """
    Observius Network Inventory (ONI) Main Process
    """
    # Configuration File Initialization
    oni_yaml_file = "resources/etc/oni/oni.yaml"
    oni_db_yaml_file = "resources/etc/databases/oni.yaml"
    oni_yaml = YamlReader(yaml_file=oni_yaml_file)
    oni_db_yaml = YamlReader(yaml_file=oni_db_yaml_file)

    # Variable Initialization
    program_name = oni_yaml.get_value("oni.settings.program_name")
    logging_level = oni_yaml.get_value("oni.settings.log_level")
    logging_path = oni_yaml.get_value("oni.settings.log_file_path")
    create_dir(path_minus_file(logging_path))

    # Logger Initialization
    logger = LoggerSetup(
        name=program_name, log_file=logging_path, level=logging_level
    ).get_logger()
    logger.info("Starting Observius Network Inventory (ONI)")
    logger.info(f'Configuration File: "{oni_yaml_file}" loaded successfully.')
    logger.info(f'Configuration File: "{oni_db_yaml_file}" loaded successfully.')

    # Database Initialization
    logger.info("Initializing ONI Database")
    oni_db = SQLiteManager(
        database_path=oni_db_yaml.get_value("database.settings.file")
    )

    # Netbox API Configuration
    secrets_path = "resources/etc/secrets/secrets.yaml"
    netbox_api_yaml_path = "resources/etc/connectors/netbox/netbox_api.yaml"
    secrets = YamlReader(yaml_file=secrets_path)
    netbox_api_config = YamlReader(yaml_file=netbox_api_yaml_path)
    base_url = netbox_api_config.get_value(path="netbox_api.base_url")
    api_token = secrets.get_value(path="secrets.netbox_api_token.api_token")
    netbox_api = NetBoxAPI(api_token=api_token, base_url=base_url)

    #############
    # Gathering #
    #############

    # Gather Interfaces
    # oni_interfaces = oni_db.execute_sqlite_query(query="SELECT * FROM interfaces", params=None)

    # Gather Devices
    oni_devices_df = oni_db.execute_sqlite_query(
        query="SELECT * FROM master_inventory", params=None
    )
    print(oni_devices_df)

    ###########
    # Loading #
    ###########

    # Load Unique IP Addresses
    for index, device in oni_devices_df.iterrows():
        if device.ipv4:
            ipv4_data = {
                "address": device.ipv4,
                "status": "active",
                "description": f"IP for device: {device.hostname}",
            }
            netbox_api.ipam_manager.create_ipv4(data=ipv4_data)

    # Load Devices
    device_objects = convert_df_to_devices(dataframe=oni_devices_df)

    for device_object in device_objects[3:4]:

        # Create the device
        netbox_device_df = device_object.device_to_netbox_dataframe()
        unknown_device_type_id = netbox_api.devicetype_manager.find_device_type_by_slug(
            "unknown"
        ).get("id")
        unknown_device_role_id = netbox_api.role_manager.find_role_by_slug(
            "unknown"
        ).get("id")
        netbox_device_df["device_type"] = unknown_device_type_id
        # netbox_device_df['primary_ip4'] = netbox_api.ipam_manager.get_netbox_id(ip_address=netbox_device_df.loc[0, 'primary_ip4'], subnet_mask=32)
        netbox_device_df["primary_ip4"] = ""
        netbox_device_df["role"] = unknown_device_role_id
        netbox_device_df["site"] = "1"
        netbox_device_df = purge_empty_values_from_dataframe(dataframe=netbox_device_df)
        netbox_api.device_manager.create_device_from_dataframe(df=netbox_device_df)

        # find the device id
        netbox_device = netbox_api.device_manager.find_device_by_name(
            name=device_object.dns_name
        )
        netbox_device_id = netbox_device["id"]

        # 2025-02-22 12:47:00
        # This is currently broken
        # I need to be able to disambiguate interfaces on the same device
        # see opennms collector, I am in the process of collecting SNMP interface names--which will need to be propagated to the OpenNMS Device Collection information table

        # create interface
        interface_data = {
            "device": netbox_device_id,
            "name": "eth0",
            "type": "1000base-t",
            "enabled": True,
            "mtu": 1500,
            "physical_address": device_object.mac,
        }
        netbox_api.interface_manager.create_interface(data=interface_data)

        # Assign the IP address to the device
        # netbox_api.device_manager.assign_ip_address_to_device(
        #     device_name=device_object.hostname, ip_address=device_object.ipv4
        # )


if __name__ == "__main__":
    main()
