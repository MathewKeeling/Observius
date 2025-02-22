import logging
import requests
import urllib3
import pandas as pd
from src.modules.yaml.YamlReader import YamlReader

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DeviceManager:
    def __init__(self, api):
        self.api = api
        self.logger = logging.getLogger(__name__)

    def create_device(self, data):
        try:
            response = self.api._post("dcim/devices/", data)
            response.raise_for_status()
            self.logger.info(f"Device created successfully: {data['name']}")
            return response.json()
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e.response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error occurred: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

    def create_device_from_yaml(self, yaml_path):
        try:
            yaml_reader = YamlReader(yaml_file=yaml_path)
            device_data = yaml_reader.read()
            return self.create_device(device_data)
        except FileNotFoundError as e:
            self.logger.error(f"YAML file not found: {e}")
        except Exception as e:
            self.logger.error(f"An error occurred while reading the YAML file: {e}")

    def create_device_from_dataframe(self, df: pd.DataFrame):
        try:
            device_data = df.to_dict(orient="records")[0]
            return self.create_device(device_data)
        except IndexError as e:
            self.logger.error(f"DataFrame is empty: {e}")
        except Exception as e:
            self.logger.error(f"An error occurred while processing the DataFrame: {e}")

    def find_device_by_name(self, name):
        """
        Find a device based on the name name.
        """
        params = {"name": name}
        try:
            devices = self.get_devices(params=params)
            if devices["count"] > 0:
                self.logger.info(f"Device found: {devices['results'][0]}")
                return devices["results"][0]
            else:
                self.logger.info(f"No device found with name: {name}")
                return None
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e.response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error occurred: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

    def get_devices(self, params=None):
        try:
            response = self.api._get("dcim/devices/", params)
            return response
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e.response.text}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error occurred: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

    def print_all_devices(self):
        devices = self.get_devices()
        if devices:
            for device in devices.get("results", []):
                self.logger.info(
                    f"Device: {device['name']}, Manufacturer: {device['manufacturer']}, Model: {device['model']}"
                )
