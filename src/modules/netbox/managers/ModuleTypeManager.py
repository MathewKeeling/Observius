from src.modules.yaml.YamlReader import YamlReader
import logging
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ModuleTypeManager:
    def __init__(self, api):
        self.api = api

    def create_module_type(self, device_module_data):
        """
        Create a module type in NetBox.

        Parameters:
            device_module_data (dict): The module data to create the module type in NetBox.
        """
        manufacturer_slug = device_module_data.get("manufacturer").lower()
        manufacturer_id = self.api.manufacturer_manager.find_manufacturer_by_slug(
            manufacturer_slug=manufacturer_slug
        )
        device_module_data["manufacturer"] = manufacturer_id
        # Check if the module already exists
        existing_module = self.find_module_type_by_model(
            model=device_module_data["model"]
        )
        if existing_module:
            logging.debug(f"Module {device_module_data['model']} already exists.")
            module_id = existing_module["id"]
            return self.api._put(f"dcim/module-types/{module_id}/", device_module_data)

        # If the module does not exist, create it
        return self.api._post("dcim/module-types/", device_module_data)

    def create_module_types_from_yaml(self, yaml_file):
        """
        Create module types in NetBox from a YAML file.

        Parameters:
            yaml_file (str): The path to the YAML file containing the module types.
        """
        modules_data = YamlReader(yaml_file=yaml_file).get_section("modules")
        if modules_data:
            for module in modules_data:
                try:
                    self.create_module(module)
                    logging.debug(f"Module created: {module['model']}")
                except requests.exceptions.RequestException as e:
                    logging.debug(f"Error creating module {module['model']}: {e}")
        else:
            logging.debug("No modules found in the YAML file.")

    def delete_module_type(self, module_id):
        """
        Delete a module type in NetBox.

        Parameters:
            module_id (int): The ID of the module type to delete.
        """
        return self.api._delete(f"dcim/module-types/{module_id}/")

    def find_module_type_by_model(self, model):
        """
        Find a module type in NetBox by model.

        Parameters:
            model (str): The model of the module type to find.
        """
        modules = self.get_all_module_types()
        for module in modules:
            if module["model"] == model:
                return module
        return None

    def get_all_module_types(self, limit=1000):
        """
        get all module types in NetBox.

        Parameters:
            limit (int): The maximum number of module types to return.
        """
        return self.api._get(f"dcim/module-types/?limit={limit}")["results"]
