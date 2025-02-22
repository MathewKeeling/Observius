import logging
import requests
from src.modules.yaml.YamlReader import YamlReader


class ManufacturerManager:
    def __init__(self, api):
        self.api = api

    def create_manufacturer(self, data):
        # Check if the manufacturer already exists by slug
        try:
            existing_manufacturer_id = self.find_manufacturer_by_slug(data.get("slug"))
            logging.debug(f"Manufacturer {data.get('name')} already exists.")
            return self.api._put(
                f"dcim/manufacturers/{existing_manufacturer_id}/", data
            )
        except ValueError:
            logging.debug(f"Creating manufacturer {data.get('name')}")
            return self.api._post("dcim/manufacturers/", data)

    def create_manufacturers_from_yaml(self, yaml_file_path):
        manufacturers_data = YamlReader(yaml_file=yaml_file_path).get_section(
            "manufacturers"
        )
        if manufacturers_data:
            for manufacturer in manufacturers_data:
                try:
                    self.create_manufacturer(manufacturer)
                    logging.debug(f"Manufacturer created: {manufacturer['name']}")
                except requests.exceptions.RequestException as e:
                    logging.debug(
                        f"Error creating manufacturer {manufacturer['name']}: {e}"
                    )
        else:
            logging.debug("No manufacturers found in the YAML file.")

    def find_manufacturer_by_slug(self, manufacturer_slug):
        response = self.api._get(f"dcim/manufacturers/?slug={manufacturer_slug}")
        manufacturers = response.get("results", [])
        if manufacturers:
            return manufacturers[0]["id"]
        else:
            raise ValueError(f"Manufacturer with slug '{manufacturer_slug}' not found.")

    def find_manufacturer_by_name(self, manufacturer_name):
        response = self.api._get(f"dcim/manufacturers/?name={manufacturer_name}")
        manufacturers = response.get("results", [])
        if manufacturers:
            return manufacturers[0]
        else:
            raise ValueError(f"Manufacturer with name '{manufacturer_name}' not found.")

    def get_manufacturers(self, params=None):
        return self.api._get("dcim/manufacturers/", params)

    def manufacturer_exists(self, slug):
        slug = slug.lower()
        manufacturers = self.get_manufacturers()
        for manufacturer in manufacturers.get("results", []):
            if manufacturer.get("slug").lower() == slug:
                return True
        return False
