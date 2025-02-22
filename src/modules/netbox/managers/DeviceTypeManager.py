import logging
import requests
import urllib3
from src.modules.yaml.YamlReader import YamlReader

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DeviceTypeManager:
    def __init__(self, api):
        self.api = api

    def create_device_type(self, data):
        response = self.api._post("dcim/device-types/", data)
        return response

    def create_device_type_from_yaml(self, yaml_file):
        device_types = YamlReader(yaml_file=yaml_file).get_section("device_types")
        if not device_types:
            logging.debug("No device types found in the YAML file.")
            return

        for device_type in device_types:
            self._process_device_type(device_type)

    def find_device_type_by_slug(self, slug):
        """
        Find a device type based on the slug name.
        """
        params = {"slug": slug}
        device_types = self.get_device_types(params=params)
        if device_types["count"] > 0:
            logging.debug(f"Device type found: {device_types['results'][0]}")
            return device_types["results"][0]
        else:
            logging.debug(f"No device type found with slug: {slug}")
            return None

    def get_device_types(self, params=None):
        return self.api._get("dcim/device-types/", params)

    def print_all_device_types(self):
        device_types = self.get_device_types()
        for device in device_types["results"]:
            logging.debug(
                f"Manufacturer: {device['manufacturer']}, Model: {device['model']}, Slug: {device['slug']}"
            )

    def _find_existing_device(self, data):
        params_list = [
            {"manufacturer": data["manufacturer"], "model": data["model"]},
            {"manufacturer": data["manufacturer"], "slug": data["slug"]},
        ]
        for params in params_list:
            existing_devices = self.get_device_types(params=params)
            if existing_devices["count"] > 0:
                logging.debug(f"Device type with {params} already exists.")
                return existing_devices["results"][0]
        return None

    def process_device_type(self, device_type):
        """
        Create a device type in NetBox from a dictionary.
        """
        try:
            manufacturer_slug = device_type.get("manufacturer").lower()
            self.create_device_type(device_type)
            logging.debug(f"Device type created: {device_type['slug']}")
        except ValueError as e:
            logging.debug(f"Manufacturer slug {manufacturer_slug} not found: {e}")
        except requests.exceptions.HTTPError as e:
            logging.debug(
                f"HTTP error creating device type {device_type['slug']}: {e.response.text}"
            )
        except requests.exceptions.RequestException as e:
            logging.debug(
                f"Request error creating device type {device_type['slug']}: {e}"
            )

    def process_device_types_from_yaml(self, yaml_file):
        """
        Process multiple device types from a single YAML file.
        """
        device_types = YamlReader(yaml_file=yaml_file).get_section("device_types")
        if not device_types:
            logging.debug("No device types found in the YAML file.")
            return

        for device_type in device_types:
            self._process_device_type(device_type)
