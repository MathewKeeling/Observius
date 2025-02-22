from src.modules.common.LoggerSetup import LoggerSetup
from src.modules.yaml.YamlReader import YamlReader
from src.modules.common.linux import create_dir, path_minus_file
from src.modules.netbox.NetBoxAPI import NetBoxAPI
from src.modules.common.linux import get_all_file_paths
import os


def main():
    """
    Observius Network Inventory (ONI) Main Process
    """
    # Configuration File Initialization
    oni_yaml_file = "resources/etc/oni/oni.yaml"
    oni_db_yaml_file = "resources/etc/databases/oni.yaml"
    oni_yaml = YamlReader(yaml_file=oni_yaml_file)

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

    # Netbox API Configuration
    secrets_path = "resources/etc/secrets/secrets.yaml"
    netbox_api_yaml_path = "resources/etc/connectors/netbox/netbox_api.yaml"
    secrets = YamlReader(yaml_file=secrets_path)
    netbox_api_config = YamlReader(yaml_file=netbox_api_yaml_path)
    base_url = netbox_api_config.get_value(path="netbox_api.base_url")
    api_token = secrets.get_value(path="secrets.netbox_api_token.api_token")
    netbox_api = NetBoxAPI(api_token=api_token, base_url=base_url)

    # Settings
    device_roles = True
    manufacturers = True
    module_types = True
    device_types = True

    # Device Roles Configuration
    if device_roles:
        roles_yaml_path = "resources/etc/connectors/netbox/config/roles.yaml"
        netbox_api.role_manager.create_roles_from_yaml(yaml_file_path=roles_yaml_path)

    # Manufacturer Configuration
    if manufacturers:
        manufacturers_yaml_path = (
            "resources/etc/connectors/netbox/config/manufacturers.yaml"
        )
        netbox_api.manufacturer_manager.create_manufacturers_from_yaml(
            yaml_file_path=manufacturers_yaml_path
        )

    # Device Modules Configuration
    if module_types:
        module_types_repo_dir = "resources/etc/connectors/netbox/config/module_types"
        for file_path in get_all_file_paths(module_types_repo_dir):
            if not file_path.endswith(".yaml"):
                continue
            else:
                device_module_data = YamlReader(yaml_file=file_path).data
                netbox_api.module_type_manager.create_module_type(
                    device_module_data=device_module_data
                )

    # Device Types Configuration
    if device_types:
        device_types_repo_dir = "resources/etc/connectors/netbox/config/device_types"
        for file_path in get_all_file_paths(device_types_repo_dir):
            if not file_path.endswith(".yaml"):
                continue
            else:
                device_type_data = YamlReader(yaml_file=file_path).data
                netbox_api.devicetype_manager.process_device_type(
                    device_type=device_type_data
                )


if __name__ == "__main__":
    main()
