from src.modules.yaml.YamlReader import YamlReader
import logging
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DeviceRoleManager:
    def __init__(self, api):
        self.api = api

    def create_role(self, data):
        # Check if the role already exists
        existing_role = self.find_role_by_name(data["name"])
        if existing_role:
            logging.debug(f"Role {data['name']} already exists.")
            role_id = existing_role["id"]
            return self.api._put(f"dcim/device-roles/{role_id}/", data)

        # If the role does not exist, create it
        return self.api._post("dcim/device-roles/", data)

    def create_roles_from_yaml(self, yaml_file_path):
        roles_data = YamlReader(yaml_file=yaml_file_path).get_section("roles")
        if roles_data:
            for role in roles_data[-1:]:
                try:
                    self.create_role(role)
                    logging.debug(f"Role created: {role['name']}")
                except requests.exceptions.RequestException as e:
                    logging.debug(f"Error creating role {role['name']}: {e}")
        else:
            logging.debug("No roles found in the YAML file.")

    def delete_role(self, role_id):
        return self.api._delete(f"dcim/device-roles/{role_id}/")

    def find_role_by_slug(self, slug):
        roles = self.api._get("dcim/device-roles/")
        for role in roles["results"]:
            if role["slug"] == slug:
                return role
        return None

    def get_all_roles(self):
        return self.api._get("dcim/device-roles/")["results"]
