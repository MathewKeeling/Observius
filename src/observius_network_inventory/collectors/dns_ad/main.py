from src.modules.yaml.YamlReader import YamlReader
from src.modules.sqlite.main import SQLiteManager
from src.modules.common.LoggerSetup import LoggerSetup
import dns.resolver
import ipaddress
import time
from src.modules.device.Device import Device, AssetRecord
import logging


def current_epoch_time():
    return int(time.time())


class DNSCollector:
    def __init__(self, db: SQLiteManager, logger: LoggerSetup):
        self.subnets_yaml = YamlReader(
            yaml_file="resources/etc/autodiscovery/subnets.yaml"
        )
        self.dns_ad_yaml = YamlReader(yaml_file="resources/etc/collectors/dns_ad.yaml")
        self.dns_servers = [
            host["ip_address"] for host in self.dns_ad_yaml.get_section("dns_ad_hosts")
        ]
        self.db = db
        self.logger = logger

    def query_dns_records(self) -> list:
        dns_results_list = []

        # Check if IPv4 is enabled and process the networks
        if self.subnets_yaml.get_value("subnets.ipv4.enabled"):
            ipv4_networks = self.subnets_yaml.get_value("subnets.ipv4.networks")
            for network in ipv4_networks:
                dns_results_list.extend(self.collect_dns_records(network["cidr"]))

        return dns_results_list

    def collect_dns_records(self, cidr: str) -> list:
        dns_records = []
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = self.dns_servers
            network = ipaddress.ip_network(cidr)
            for ip in network.hosts():
                try:
                    answers = resolver.resolve(ip.reverse_pointer, "PTR")
                    for rdata in answers:
                        hostname = (
                            rdata.to_text().rstrip(".").upper()
                        )  # Remove trailing period and convert to uppercase
                        dns_records.append(
                            {"ipv4": str(ip).upper(), "hostname": hostname}
                        )
                except dns.resolver.NXDOMAIN:
                    self.logger.debug(f"No PTR record found for {ip}")
                except Exception as e:
                    self.logger.error(f"Error collecting DNS records for {ip}: {e}")
        except Exception as e:
            self.logger.error(f"Error processing cidr {cidr}: {e}")
        return dns_records

    def dns_collection(self):
        dns_results = self.query_dns_records()
        for result in dns_results:
            ipv4 = result.get("ipv4").upper()
            if ipv4:
                # Ensure 'first_seen' and 'last_seen' keys are set
                result.setdefault("first_seen", current_epoch_time())
                result.setdefault("last_seen", current_epoch_time())

                # Check if the IPv4 address already exists in the database
                query = "SELECT COUNT(*) FROM source_dns_ad WHERE ipv4 = ?"
                db_result = self.db.execute_sqlite_command(query, (ipv4,))
                count = db_result[0][0]

                if count > 0:
                    # Update the last_seen time
                    update_query = """
                        UPDATE source_dns_ad
                        SET last_seen = ?
                        WHERE ipv4 = ?
                    """
                    self.db.execute_sqlite_command(
                        update_query, (current_epoch_time(), ipv4)
                    )
                else:
                    # Insert new record with first_seen and last_seen times
                    dns_insert_query = self.db.build_insert_command(
                        table_name="source_dns_ad", data=result
                    )
                    self.db.execute_sqlite_command(
                        dns_insert_query[0], dns_insert_query[1]
                    )

                # Create a Device instance
                device_data = {
                    "ipv4": result["ipv4"],
                    "mac": "",  # Placeholder, update with actual MAC if available
                    "serial_number": None,
                    "manufacturer": None,
                    "dns_name": result["hostname"],
                    "metadata": {},
                    "location": "",
                    "categories": [],
                    "foreignSource": "",
                    "assetRecord": AssetRecord(
                        category="Unspecified",
                        id="",
                    ),
                    "foreignId": "",
                    "first_seen": result["first_seen"],
                    "lastIngressFlow": None,
                    "lastEgressFlow": None,
                    "labelSource": "",
                    "last_seen": result["last_seen"],
                    "type": "",
                    "id": "",
                }
                device = Device(**device_data)
                logging.debug(device)
            else:
                self.logger.error("IPv4 address not found in result")


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

    collector = DNSCollector(db=db, logger=logger)
    collector.dns_collection()
