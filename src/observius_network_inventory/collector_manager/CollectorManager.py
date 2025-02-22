from src.observius_network_inventory.collectors.dns_ad.main import DNSCollector
from src.observius_network_inventory.collectors.opennms.import_opennms_devices import (
    OpenNMSCollector,
)
from src.observius_network_inventory.collectors.snmp.main import snmp_collection
from src.observius_network_inventory.collectors.unifi_controller_api.main import (
    unifi_collection,
)
from src.observius_network_inventory.collectors.unifi_network_api.UnifiNetworkAPICollector import (
    UniFiNetworkAPICollector,
)
from src.modules.yaml.YamlReader import YamlReader
from src.modules.sqlite.main import SQLiteManager
from src.modules.common.LoggerSetup import LoggerSetup


class CollectorManager:
    """A class to manage and run various network inventory collectors."""

    def __init__(self, db: SQLiteManager, logger: LoggerSetup):
        """Initialize the CollectorManager with the database manager and logger.
        :param db: An instance of SQLiteManager to manage database operations.
        :param logger: An instance of LoggerSetup for logging.
        """
        self.config_path = "resources/etc/oni/oni.yaml"
        self.oni_config = YamlReader(self.config_path)
        self.collectors = self.load_config()
        self.logger = logger
        self.db = db

    def load_config(self):
        """Load the collector configurations from the YAML file.
        :return: A dictionary containing the collector configurations.
        """
        return self.oni_config.get_section("oni.collectors") or {}

    def run_collectors(self):
        """Run all enabled collectors as specified in the configuration."""
        for collector_name, config in self.collectors.items():
            if config.get("enabled", False):
                self.run_collector(collector_name)

    def run_collector(self, collector_name):
        """Run a specific collector based on its name.
        :param collector_name: The name of the collector to run.
        """
        collectors_map = {
            "dns_ad": DNSCollector(db=self.db, logger=self.logger).dns_collection,
            "snmp": lambda: snmp_collection(oni_db=self.db),
            "opennms": OpenNMSCollector(db=self.db, logger=self.logger).collect_data,
            "unifi_controller_api": lambda: unifi_collection(oni_db=self.db),
            "unifi_network_api": UniFiNetworkAPICollector(
                db=self.db, logger=self.logger
            ).collect_data,
        }

        placeholders = [
            "arp",
            "dhcp_logs",
            "esxi",
            "fs_network",
            "hyperv",
            "kvm",
            "nmap",
            "proxmox",
            "vcenter",
            "xcpng",
        ]

        try:
            self.logger.info(f"Running collector: {collector_name}")
            collector_func = collectors_map.get(collector_name)
            if collector_func:
                collector_func()
            elif collector_name in placeholders:
                self.logger.info(f"Running collector: {collector_name}")
                print(f"Collector {collector_name} is not implemented.")
                pass
            else:
                self.logger.info(f"Collector {collector_name} is not implemented.")
        except Exception as e:
            self.logger.error(f"Error running collector {collector_name}: {e}")


if __name__ == "__main__":
    print()
