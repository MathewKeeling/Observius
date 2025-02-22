import logging
import requests
from src.modules.yaml.YamlReader import YamlReader


class InterfaceManager:
    def __init__(self, api):
        self.api = api

    def create_interface(self, data):
        # Check if the interface already exists by name
        try:
            existing_interface_id = self.find_interface_by_mac(
                data.get("physical_address")
            )
            logging.debug(f"Interface {data.get('name')} already exists.")
            return self.api._put(f"dcim/interfaces/{existing_interface_id}/", data)
        except ValueError:
            logging.debug(f"Creating interface {data.get('name')}")
            return self.api._post("dcim/interfaces/", data)

    def create_interfaces_from_yaml(self, yaml_file):
        interfaces_data = YamlReader(yaml_file=yaml_file).get_section("interfaces")
        if interfaces_data:
            for interface in interfaces_data:
                try:
                    self.create_interface(interface)
                    logging.debug(f"Interface created: {interface['name']}")
                except requests.exceptions.RequestException as e:
                    logging.debug(f"Error creating interface {interface['name']}: {e}")
        else:
            logging.debug("No interfaces found in the YAML file.")

    def find_interface_by_mac(self, physical_address):
        response = self.api._get(
            f"dcim/interfaces/?physical_address={physical_address}"
        )
        interfaces = response.get("results", [])
        if interfaces:
            return interfaces[0]["id"]
        else:
            raise ValueError(
                f"Interface with MAC address '{physical_address}' not found"
            )

    def find_interface_by_name(self, interface_name):
        response = self.api._get(f"dcim/interfaces/?name={interface_name}")
        interfaces = response.get("results", [])
        if interfaces:
            return interfaces[0]["id"]
        else:
            raise ValueError(f"Interface with name '{interface_name}' not found.")

    def get_interfaces(self, params=None):
        return self.api._get("dcim/interfaces/", params)

    def interface_exists(self, name):
        name = name.lower()
        interfaces = self.get_interfaces()
        for interface in interfaces.get("results", []):
            if interface.get("name").lower() == name:
                return True
        return False
