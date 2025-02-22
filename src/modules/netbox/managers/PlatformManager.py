from src.modules.yaml.YamlReader import YamlReader
import logging
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PlatformManager:
    def __init__(self, api):
        self.api = api

    def create_platform(self, data):
        # Get Manufacturing ID
        if "manufacturer" in data:
            manufacturer = self.api.manufacturer_manager.find_manufacturer_by_name(
                data["manufacturer"]
            )
            data["manufacturer"] = manufacturer["id"]

        # Check if the platform already exists
        existing_platform = self.find_platform_by_name(data["name"])
        if existing_platform:
            logging.debug(f"Platform {data['name']} already exists.")
            platform_id = existing_platform["id"]
            return self.api._put(f"dcim/platforms/{platform_id}/", data)

        # If the platform does not exist, create it
        return self.api._post("dcim/platforms/", data)

    def create_platforms_from_yaml(self, yaml_file):
        platforms_data = YamlReader(yaml_file=yaml_file).get_section("platforms")
        if platforms_data:
            for platform in platforms_data[-1:]:
                try:
                    self.create_platform(platform)
                    logging.debug(f"Platform created: {platform['name']}")
                except requests.exceptions.RequestException as e:
                    logging.debug(f"Error creating platform {platform['name']}: {e}")
        else:
            logging.debug("No platforms found in the YAML file.")

    def delete_platform(self, platform_id):
        return self.api._delete(f"dcim/platforms/{platform_id}/")

    def find_platform_by_name(self, name):
        platforms = self.api._get("dcim/platforms/")
        for platform in platforms["results"]:
            if platform["name"] == name:
                return platform
        return None

    def get_all_platforms(self):
        return self.api._get("dcim/platforms/")["results"]
