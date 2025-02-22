import logging
import requests
import urllib3
import ipaddress
from src.modules.yaml.YamlReader import YamlReader

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class IPAMManager:
    def __init__(self, api):
        self.api = api
        self.logger = logging.getLogger(__name__)
        self.autodiscovery_yaml_path = "resources/etc/autodiscovery/subnets.yaml"
        self.autodiscovery_yaml = YamlReader(yaml_file=self.autodiscovery_yaml_path)

    def create_ipv4(self, data):
        existing_ip = self.get_ipv4_address(data["address"])
        if existing_ip:
            self.logger.info(
                f"IPv4 address {data['address']} already exists. Updating instead."
            )
            return self.update_ipv4(existing_ip["id"], data)
        try:
            response = self.api._post("ipam/ip-addresses/", data)
            self.logger.info(f"IPv4 address created successfully: {data['address']}")
            return response.json()
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e.response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error occurred: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

    def create_ip_range(self, data):
        try:
            response = self.api._post("ipam/ip-ranges/", data)
            self.logger.info(f"IP range created successfully: {data['description']}")
            return response.json()
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e.response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error occurred: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

    def delete_ipv4(self, ip_address, subnet_mask):
        try:
            netbox_id = self.get_netbox_id(ip_address, subnet_mask)
            if netbox_id:
                response = self.api._delete(f"ipam/ip-addresses/{netbox_id}/")
                self.logger.info(f"IPv4 address deleted successfully: {ip_address}")
                return response.json()
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e.response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error occurred: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

    def get_ipv4_address(self, address):
        try:
            params = {"address": address}
            response = self.api._get("ipam/ip-addresses/", params)
            results = response.get("results", [])
            if results:
                return results[0]
            self.logger.info(f"No IPv4 address found for: {address}")
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e.response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error occurred: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
        return None

    def get_netbox_id(self, ip_address, subnet_mask) -> int:
        """
        Get the NetBox ID for an IP address

        args:
            ip_address (str): IP address
            subnet_mask (int): Subnet mask
        returns:
            int: NetBox ID
        """
        try:
            network = ipaddress.IPv4Network(f"{ip_address}/{subnet_mask}", strict=False)
            for ip in network.hosts():
                params = {"address": str(ip)}
                response = self.api._get("ipam/ip-addresses/", params)
                results = response.get("results", [])
                if results:
                    return results[0].get("id")
            self.logger.info(
                f"No NetBox ID found for IP address: {ip_address} with subnet mask: {subnet_mask}"
            )
        except ValueError as e:
            self.logger.error(f"Invalid IP address or subnet mask: {e}")
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e.response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error occurred: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

        return None

    def init_create_ips(self) -> None:
        try:
            config = self.autodiscovery_yaml

            if config.get_section("subnets")["ipv4"]["enabled"]:
                for network in config.get_section("subnets.ipv4.networks"):
                    cidr = network["cidr"]
                    network_obj = ipaddress.IPv4Network(cidr, strict=False)
                    for ip in network_obj.hosts():
                        data = {"address": str(ip)}
                        self.create_ipv4(data)
        except config.YAMLError as e:
            self.logger.error(f"Error parsing YAML file: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

    def init_create_ip_ranges(self) -> None:
        try:
            config = self.autodiscovery_yaml

            if config.get_section("subnets")["ipv4"]["enabled"]:
                for network in config.get_section("subnets.ipv4.networks"):
                    cidr = network["cidr"]
                    description = network.get("description", "")
                    network_obj = ipaddress.IPv4Network(cidr, strict=False)
                    data = {
                        "description": description,
                        "start_address": str(network_obj.network_address),
                        "end_address": str(network_obj.broadcast_address),
                        "cidr": cidr,
                    }
                    self.create_ip_range(data)
        except config.YAMLError as e:
            self.logger.error(f"Error parsing YAML file: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

    def print_all_ipv4_addresses(self) -> None:
        ipv4_addresses = self.get_ipv4_addresses()
        if ipv4_addresses:
            for ip in ipv4_addresses.get("results", []):
                self.logger.info(
                    f"IPv4 Address: {ip['address']}, Status: {ip['status']}"
                )

    def print_all_ipv4_addresses(self) -> None:
        ipv4_addresses = self.get_ipv4_addresses()
        if ipv4_addresses:
            for ip in ipv4_addresses.get("results", []):
                self.logger.info(
                    f"IPv4 Address: {ip['address']}, Status: {ip['status']}"
                )

    def update_ipv4(self, ip_id, data):
        try:
            response = self.api._put(f"ipam/ip-addresses/{ip_id}/", data)
            self.logger.info(f"IPv4 address updated successfully: {data['address']}")
            return response
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e.response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error occurred: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
