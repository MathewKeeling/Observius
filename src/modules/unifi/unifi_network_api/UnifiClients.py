import logging
from src.modules.yaml.YamlReader import YamlReader
from src.modules.unifi.unifi_network_api.UniFiAPI import UniFiAPI
from src.modules.device.Device import Device, AssetRecord
from datetime import datetime, timezone
from src.observius_network_inventory.collectors.dns_ad.main import DNSCollector
import dns.resolver


class UnifiClients:
    def __init__(self):
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

        # Initialize logger
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.dns_collector = DNSCollector(db=None, logger=self.logger)

    def convert_clients_to_devices(self, clients: list[dict]):
        devices = []
        for client in clients:
            device = Device(
                ipv4=client.get("ipAddress", ""),
                mac=client.get("macAddress", ""),
                dns_name=client.get("name", ""),
                location=client.get("site_name", ""),
                categories=[],
                foreignSource="Unifi",
                assetRecord=AssetRecord(
                    category="Network Device", id=client.get("macAddress", "")
                ),
                foreignId=client.get("macAddress", ""),
                first_seen=self.convert_timestamp_to_unix(
                    client.get("connectedAt", "")
                ),
                last_seen=self.convert_timestamp_to_unix(client.get("connectedAt", "")),
                labelSource="Unifi",
                type="Client",
                id=client.get("id", ""),
            )
            devices.append(device)
        return devices

    def convert_devices_to_clients(self, devices: list[Device]):
        clients = []
        for device in devices:
            client = {
                "ipAddress": device.ipv4,
                "macAddress": device.mac,
                "name": device.dns_name,
                "site_name": device.location,
                "connectedAt": self.convert_unix_to_timestamp(device.first_seen),
                "id": device.id,
            }
            clients.append(client)
        return clients

    def convert_timestamp_to_unix(self, timestamp_str):
        """Convert timestamp string to Unix timestamp."""
        return int(datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ").timestamp())

    def convert_unix_to_timestamp(self, unix_timestamp):
        """Convert Unix timestamp to timestamp string."""
        return datetime.fromtimestamp(unix_timestamp, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

    def get_sites(self):
        sites = self.unifi_api.get_sites()
        return sites

    def get_clients(self, site_id: str):
        unifi_clients = self.unifi_api.get_clients(site_id=site_id)
        return unifi_clients

    def update_client_names_for_site(self, site_id: str):
        clients = self.get_clients(site_id)["data"]
        clients_as_devices = self.convert_clients_to_devices(clients)
        updated_clients = []
        for device in clients_as_devices:
            if device.ipv4 != "":
                self.logger.info(
                    f"Device {device.dns_name} has IP address {device.ipv4}"
                )
                try:
                    new_hostname = self.dns_collector.collect_dns_records(
                        cidr=device.ipv4
                    )[0]["hostname"]
                    device.dns_name = new_hostname
                except (dns.resolver.NXDOMAIN, IndexError) as e:
                    self.logger.info(
                        f"No PTR record found for IP address {device.ipv4}. Hostname will not be changed."
                    )
            else:
                self.logger.debug(f"Device {device.dns_name} has no IP address")
            updated_clients.append(device)

        new_client_data = self.convert_devices_to_clients(updated_clients)
        for client in new_client_data:
            if client["name"] != "":
                self.update_client_hostname(client_data=client, site_id=site_id)

    def update_client_hostname(self, client_data: dict, site_id: str):
        self.unifi_api.update_client_name(
            site_id=site_id,
            client_id=client_data["id"],
            client_name=client_data["name"],
        )


if __name__ == "__main__":
    unifi_api = UnifiClients()
    sites = unifi_api.get_sites()
    for site in sites["data"]:
        unifi_api.update_client_names_for_site(site_id=site["id"])
