from src.modules.netbox.managers.DeviceManager import DeviceManager
from src.modules.netbox.managers.DeviceRoleManager import DeviceRoleManager
from src.modules.netbox.managers.DeviceTypeManager import DeviceTypeManager
from src.modules.netbox.managers.InterfaceManager import InterfaceManager
from src.modules.netbox.managers.ModuleTypeManager import ModuleTypeManager
from src.modules.netbox.managers.IPAMManager import IPAMManager
from src.modules.netbox.managers.ManufacturerManager import ManufacturerManager
from src.modules.netbox.managers.OrganizationManager import OrganizationManager
from src.modules.netbox.managers.PlatformManager import PlatformManager
import logging
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NetBoxAPI:
    def __init__(self, api_token: str, base_url: str):
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Token {api_token}",
            "Accept": "application/json",
        }
        self.device_manager = DeviceManager(self)
        self.devicetype_manager = DeviceTypeManager(self)
        self.interface_manager = InterfaceManager(self)
        self.ipam_manager = IPAMManager(self)
        self.manufacturer_manager = ManufacturerManager(self)
        self.module_type_manager = ModuleTypeManager(self)
        self.organization_manager = OrganizationManager(self)
        self.platform_manager = PlatformManager(self)
        self.role_manager = DeviceRoleManager(self)

    def _delete(self, endpoint: str):
        url = f"{self.base_url}/api/{endpoint}"
        response = requests.delete(url, headers=self.headers, verify=False)
        logging.debug(f"Request URL: {url}")
        logging.debug(f"Headers: {self.headers}")
        logging.debug(f"Response Status Code: {response.status_code}")
        logging.debug(f"Response Content: {response.content}")

        response.raise_for_status()  # Ensure this raises an HTTPError for bad responses
        return response.status_code  # Return the status code to confirm deletion

    def _get(self, endpoint: str, params=None):
        url = f"{self.base_url}/api/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        logging.debug(f"Request URL: {url}")
        logging.debug(f"Headers: {self.headers}")
        logging.debug(f"Params: {params}")
        logging.debug(f"Response Status Code: {response.status_code}")
        logging.debug(f"Response Content: {response.content}")

        response.raise_for_status()  # Ensure this raises an HTTPError for bad responses
        return response.json()

    def _post(self, endpoint: str, data=None):
        url = f"{self.base_url}/api/{endpoint}"
        response = requests.post(url, headers=self.headers, json=data, verify=False)
        logging.debug(f"Request URL: {url}")
        logging.debug(f"Headers: {self.headers}")
        logging.debug(f"Data: {data}")
        logging.debug(f"Response Status Code: {response.status_code}")
        logging.debug(f"Response Content: {response.content}")

        response.raise_for_status()  # Ensure this raises an HTTPError for bad responses
        return response  # Return the response object instead of response.json()

    def _put(self, endpoint: str, data=None):
        url = f"{self.base_url}/api/{endpoint}"
        response = requests.put(url, headers=self.headers, json=data, verify=False)
        logging.debug(f"Request URL: {url}")
        logging.debug(f"Headers: {self.headers}")
        logging.debug(f"Data: {data}")
        logging.debug(f"Response Status Code: {response.status_code}")
        logging.debug(f"Response Content: {response.content}")

        response.raise_for_status()  # Ensure this raises an HTTPError for bad responses
        return response.json()

    # Search methods

    @staticmethod
    def search_items(items, search_term):
        matching_items = []
        for item in items["results"]:
            if any(
                search_term.lower() in str(value).lower() for value in item.values()
            ):
                matching_items.append(item)
        return matching_items

    @staticmethod
    def find_site_by_name(sites_json, site_name):
        for site in sites_json.get("results", []):
            if site.get("name").lower() == site_name.lower():
                return site
        return None
