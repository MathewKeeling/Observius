import re
import time
import requests
from src.modules.yaml.YamlReader import YamlReader
from src.modules.sqlite.main import SQLiteManager
from src.modules.common.LoggerSetup import LoggerSetup
from src.modules.networking.mac_address import format_physical_address
from src.modules.unifi.unifi_network_api.UniFiAPI import UniFiAPI


def current_epoch_time():
    return int(time.time())


class UniFiNetworkAPICollector:
    def __init__(self, db: SQLiteManager, logger: LoggerSetup):
        self.db = db
        self.logger = logger
        self.secrets_path = "resources/etc/secrets/secrets.yaml"
        self.unifi_network_api_yaml_path = (
            "resources/etc/collectors/unifi_network_api.yaml"
        )
        self.secrets = YamlReader(yaml_file=self.secrets_path)
        self.unifi_network_api_config = YamlReader(
            yaml_file=self.unifi_network_api_yaml_path
        )
        self.server = self.unifi_network_api_config.get_value(
            path="unifi_network_api.server"
        ).upper()
        self.port = self.unifi_network_api_config.get_value(
            path="unifi_network_api.port"
        )
        self.api_key = self.secrets.get_value(
            path="secrets.unifi_network_api_token.api_token"
        )
        self.unifi_api = UniFiAPI(api_key=self.api_key, ip=self.server, port=self.port)

    def collect_data(self):
        try:
            sites = self.unifi_api.get_sites()
            self.logger.info("Sites retrieved successfully.")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error retrieving sites: {e}")
            return

        site_id = self.unifi_api.find_site_by_name(sites, "Default")["id"]

        try:
            clients = self.unifi_api.get_clients(site_id=site_id)
            self.logger.info("Clients retrieved successfully.")
            self.store_data(clients, "client")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error retrieving clients: {e}")

        try:
            devices = self.unifi_api.get_devices(site_id=site_id)
            self.logger.info("Devices retrieved successfully.")
            self.store_data(devices, "device")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error retrieving devices: {e}")

    def store_data(self, items, item_type):
        for item in items.get("data", []):
            physical_address = item.get("macAddress", "").replace("::", ":").upper()
            data = {
                "ipv4": item.get("ipAddress", "").upper(),
                "ipv6": "",
                # Disabling for now. Unifi Network API is very unreliable for this field.
                # In addition: the API does not allow updating this field.
                # "hostname": item.get("name", "").upper(),
                "hostname": "",
                "physical_address": physical_address,
                "interface_name": (
                    item.get("interfaces", [])[0].upper()
                    if item.get("interfaces")
                    else ""
                ),
                "guid_hash": "",
                "description": item.get("model", "").upper(),
                "device_type": item_type,
                "vendor": "",
                "first_seen": current_epoch_time(),
                "last_seen": current_epoch_time(),
            }
            self.insert_or_update_data("source_unifi_network_api", data)

    def insert_or_update_data(self, table_name, data):
        data = {k: v for k, v in data.items() if v}
        if "ipv4" in data:
            keys = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            values = tuple(data.values())
            query = f"""
                INSERT INTO {table_name} ({keys}) VALUES ({placeholders})
                ON CONFLICT(physical_address, ipv4) DO UPDATE SET {', '.join([f"{key}=excluded.{key}" for key in data.keys() if key not in ('physical_address', 'ipv4')])}
            """
            self.db.execute_sqlite_command(query, values)


if __name__ == "__main__":
    oni_yaml_file = "resources/etc/oni/oni.yaml"
    oni_db_yaml_file = "resources/etc/databases/oni.yaml"
    oni_yaml = YamlReader(yaml_file=oni_yaml_file)
    oni_db_yaml = YamlReader(yaml_file=oni_db_yaml_file)
    db = SQLiteManager(database_path="resources/db/oni.db")

    program_name = oni_yaml.get_value("oni.settings.program_name")
    logging_level = oni_yaml.get_value("oni.settings.log_level")
    logging_path = oni_yaml.get_value("oni.settings.log_file_path")
    logger = LoggerSetup(
        name=program_name, log_file=logging_path, level=logging_level
    ).get_logger()

    collector = UniFiNetworkAPICollector(db=db, logger=logger)
    collector.collect_data()
