from src.modules.common.LoggerSetup import LoggerSetup
from src.modules.yaml.YamlReader import YamlReader
from src.modules.sqlite.main import SQLiteManager
from src.modules.common.linux import create_dir, path_minus_file
from src.modules.device.Asset import AssetRecord
from src.modules.device.Device import (
    Device,
    convert_df_to_devices,
)
from src.modules.netbox.NetBoxAPI import NetBoxAPI
import pandas as pd


def find_blank_ipv4_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Searches the DataFrame and returns the rows where ipv4 is blank.
    """
    blank_ipv4_rows = dataframe[
        dataframe["ipv4"].isnull() | (dataframe["ipv4"].str.strip() == "")
    ]
    return blank_ipv4_rows


def update_dataframe_value(dataframe, column_name, value):
    # Fill NaN values with the provided value
    dataframe[column_name] = dataframe[column_name].apply(
        lambda x: value if pd.isna(x) else x
    )

    # Replace empty strings with the provided value
    dataframe.loc[dataframe[column_name] == "", column_name] = value

    # Handle lists by filling NaN values within lists
    if isinstance(value, list):
        dataframe[column_name] = dataframe[column_name].apply(
            lambda x: value if pd.isna(x) else x
        )


def drop_columns_with_nulls(df):
    # Drop columns with any None, NaN, or blank values
    df = df.dropna(axis=1, how="any")
    df = df.loc[:, (df != "").all(axis=0)]
    return df


def main():
    """
    Observius Network Inventory (ONI) Netbox Connector
    """
    # Configuration File Initialization
    oni_yaml_file = "resources/etc/oni/oni.yaml"
    oni_db_yaml_file = "resources/etc/databases/oni.yaml"
    oni_yaml = YamlReader(yaml_file=oni_yaml_file)
    oni_db_yaml = YamlReader(yaml_file=oni_db_yaml_file)
    netbox_connector_yaml_file = "resources/etc/connectors/netbox/netbox_api.yaml"
    netbox_connector_yaml = YamlReader(yaml_file=netbox_connector_yaml_file)

    # Variable Initialization
    program_name = netbox_connector_yaml.get_value("netbox_api.settings.program_name")
    logging_level = netbox_connector_yaml.get_value("netbox_api.settings.log_level")
    logging_path = oni_yaml.get_value("oni.settings.log_file_path")
    create_dir(path_minus_file(logging_path))

    # Logger Initialization
    logger = LoggerSetup(
        name=program_name, log_file=logging_path, level=logging_level
    ).get_logger()
    logger.info("Starting Observius Network Inventory (ONI): NetBox Collector")
    logger.info(f'Configuration File: "{oni_yaml_file}" loaded successfully.')
    logger.info(f'Configuration File: "{oni_db_yaml_file}" loaded successfully.')

    # Database Initialization
    logger.info("Initializing ONI Database")
    oni_db = SQLiteManager(
        database_path=oni_db_yaml.get_value("database.settings.file")
    )

    # Netbox Initialization
    secrets_path = "resources/etc/secrets/secrets.yaml"
    netbox_api_yaml_path = "resources/etc/connectors/netbox/netbox_api.yaml"
    secrets = YamlReader(yaml_file=secrets_path)
    netbox_api_config = YamlReader(yaml_file=netbox_api_yaml_path)

    base_url = netbox_api_config.get_value(path="netbox_api.base_url")
    api_token = secrets.get_value(path="secrets.netbox_api_token.api_token")

    netbox_api = NetBoxAPI(api_token=api_token, base_url=base_url)

    # Netbox Integration
    oni_devices_df = oni_db.execute_sqlite_query("select * from master_inventory")
    oni_device_objects = convert_df_to_devices(oni_devices_df)

    # Send devices into Netbox.
    # Assigning 'Unknown' for the Device Type and Device Role

    for device in oni_device_objects[:5]:
        netbox_device_dataframe = device.device_to_dataframe()

        # Update the 'device_type' column to 'Unknown' if it is None or empty
        update_dataframe_value(netbox_device_dataframe, "device_type", 44)
        update_dataframe_value(netbox_device_dataframe, "role", 73)
        update_dataframe_value(netbox_device_dataframe, "manufacturer", "unknown")
        update_dataframe_value(netbox_device_dataframe, "site", 1)

        cleaned_dataframe = drop_columns_with_nulls(netbox_device_dataframe)

        print("Device Dataframe: \n", cleaned_dataframe)
        # netbox_api.device_manager.create_device_from_dataframe(cleaned_dataframe)

    # print("Device Objects: \n", oni_device_objects)


if __name__ == "__main__":
    main()
