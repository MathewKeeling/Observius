import re
import time
import logging
from src.modules.yaml.YamlReader import YamlReader
from src.modules.networking.mac_address import format_physical_address
from src.modules.opennms.nodes.common import (
    onms_get_all_nodes,
    onms_get_ipinterfaces_for_id,
)
from src.modules.opennms.interfaces.interfaces import (
    get_all_ip_interfaces,
    get_all_snmp_interfaces,
)
from src.modules.sqlite.main import SQLiteManager
from src.modules.common.LoggerSetup import LoggerSetup
from src.modules.device.Device import Device


def current_epoch_time():
    return int(time.time())


class OpenNMSCollector:
    def __init__(self, db: SQLiteManager, logger: LoggerSetup):
        self.db = db
        self.logger = logger
        self.oni_config = YamlReader(yaml_file="resources/etc/oni/oni.yaml")
        self.opennms_config = YamlReader(
            yaml_file=self.oni_config.get_section("oni.collectors.opennms.config_file")
        )
        self.secrets = YamlReader(yaml_file="resources/etc/secrets/secrets.yaml")
        self.server = self.opennms_config.get_value("opennms.server")
        self.username = self.secrets.get_value(
            "secrets.opennms_autodiscovery_service_account.username"
        )
        self.password = self.secrets.get_value(
            "secrets.opennms_autodiscovery_service_account.password"
        )

    def collect_ip_interfaces(self):
        ip_interfaces = get_all_ip_interfaces(
            server=self.server, username=self.username, password=self.password
        )
        return ip_interfaces

    def collect_snmp_interfaces(self):
        snmp_interfaces = get_all_snmp_interfaces(
            server=self.server, username=self.username, password=self.password
        )
        return snmp_interfaces

    def collect_data(self):
        nodes = onms_get_all_nodes(
            server=self.server, username=self.username, password=self.password
        )
        self.store_data(nodes)

    @staticmethod
    def map_device_to_db(device: Device):
        return {
            "ipv4": device.ipv4,
            "ipv6": None,
            "hostname": device.dns_name,
            "physical_address": device.mac,
            "interface_name": None,
            "guid_hash": device.id,
            # "description": device.assetRecord.description,
            "device_type": device.type,
            "vendor": device.manufacturer,
            "first_seen": device.first_seen,
            "last_seen": device.last_seen,
        }

    def store_data(self, nodes):
        for node in nodes.get("node", []):
            node_id = node.get("id")
            ip_interfaces = onms_get_ipinterfaces_for_id(
                server=self.server,
                username=self.username,
                password=self.password,
                id=node_id,
            )

            for ip_interface in ip_interfaces.get("ipInterface", []):
                label = node.get("label", "")
                if self.is_ipv4_address(label):
                    label = ""

                device_data = self.create_device_data(node, ip_interface, label)
                logging.debug(device_data)
                device = Device(**device_data)
                data = self.map_device_to_db(device)
                self.insert_or_update_data("source_opennms", data)

    @staticmethod
    def create_device_data(node, ip_interface, label):
        return {
            "ipv4": ip_interface.get("ipAddress", "").upper(),
            "mac": format_physical_address(
                ip_interface.get("snmpInterface", {}).get("physAddr", "").upper()
            ),
            "serial_number": None,
            "manufacturer": (
                node.get("assetRecord", {}).get("vendor", "") or ""
            ).upper(),
            "dns_name": label.upper(),
            "metadata": {},
            "location": node.get("location", "").upper(),
            "categories": node.get("categories", []),
            "foreignSource": node.get("foreignSource", "").upper(),
            "assetRecord": {
                "category": node.get("assetRecord", {}).get("category", "").upper(),
                "password": None,
                "port": None,
                "id": str(node.get("assetRecord", {}).get("id", "")),
                "operatingSystem": None,
                "description": (
                    node.get("assetRecord", {}).get("description") or ""
                ).upper(),
                "username": None,
                "vendor": (node.get("assetRecord", {}).get("vendor") or "").upper(),
                "modelNumber": None,
                "manufacturer": (
                    node.get("assetRecord", {}).get("manufacturer") or ""
                ).upper(),
                "serialNumber": None,
                "circuitId": None,
                "assetNumber": None,
                "rack": None,
                "slot": None,
                "division": None,
                "department": None,
                "building": (node.get("assetRecord", {}).get("building") or "").upper(),
                "floor": None,
            },
            "foreignId": node.get("foreignId", ""),
            "first_seen": node.get("createTime", current_epoch_time()),
            "lastIngressFlow": None,
            "lastEgressFlow": None,
            "labelSource": node.get("labelSource", "").upper(),
            "last_seen": current_epoch_time(),
            "type": node.get("type", "").upper(),
            "id": node.get("id", ""),
        }

    @staticmethod
    def is_ipv4_address(label):
        return bool(re.match(r"^(\d{1,3}\.){3}\d{1,3}$", label))

    def insert_or_update_data(self, table_name, data):
        data = {k: v for k, v in data.items() if v}
        if "ipv4" in data:
            keys = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            values = tuple(data.values())
            query = f"""
            INSERT INTO {table_name} ({keys}) VALUES ({placeholders})
            ON CONFLICT(physical_address, ipv4) DO UPDATE SET
            {', '.join([f"{key}=excluded.{key}" for key in data.keys() if key not in ('physical_address', 'ipv4')])}
            """
            self.db.execute_sqlite_command(query, values)


if __name__ == "__main__":
    oni_yaml = YamlReader(yaml_file="resources/etc/oni/oni.yaml")
    db = SQLiteManager(database_path="resources/db/oni.db")
    logger = LoggerSetup(
        name=oni_yaml.get_value("oni.settings.program_name"),
        log_file=oni_yaml.get_value("oni.settings.log_file_path"),
        level=oni_yaml.get_value("oni.settings.log_level"),
    ).get_logger()
    collector = OpenNMSCollector(db=db, logger=logger)
    nodes = collector.collect_data()
    ip_interfaces = collector.collect_ip_interfaces()
    snmp_interfaces = collector.collect_snmp_interfaces()
    print(nodes)
