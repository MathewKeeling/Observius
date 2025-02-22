from src.modules.yaml.YamlReader import YamlReader
import logging
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class UniFiAPI:
    def __init__(self, api_key: str, ip: str, port="443"):
        self.api_key = api_key
        self.ip = ip
        self.port = port
        self.headers = {"X-API-KEY": api_key, "Accept": "application/json"}

    def _get(self, endpoint: str, params=None):
        base_url = f"https://{self.ip}/proxy/network/integrations/v1/{endpoint}"
        response = requests.get(
            base_url,
            headers=self.headers,
            params=params,
            verify=False,
        )
        logging.debug(f"Request URL: {base_url}")
        logging.debug(f"Headers: {self.headers}")
        logging.debug(f"Params: {params}")
        logging.debug(f"Response Status Code: {response.status_code}")
        logging.debug(f"Response Content: {response.content}")

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def _post(self, endpoint: str, data=None):
        base_url = f"https://{self.ip}/proxy/network/integrations/v1/{endpoint}"
        response = requests.put(
            base_url,
            headers=self.headers,
            json=data,
            verify=False,
        )
        logging.debug(f"Request URL: {base_url}")
        logging.debug(f"Headers: {self.headers}")
        logging.debug(f"Data: {data}")
        logging.debug(f"Response Status Code: {response.status_code}")
        logging.debug(f"Response Content: {response.content}")

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_sites(self):
        return self._get("sites")

    def get_clients(self, site_id: str, offset=0, limit=1000):
        params = {"offset": offset, "limit": limit}
        return self._get(f"sites/{site_id}/clients", params)

    def get_devices(self, site_id: str, offset=0, limit=1000):
        params = {"offset": offset, "limit": limit}
        return self._get(f"sites/{site_id}/devices", params)

    def update_client_name(self, site_id: str, client_id: str, client_name: str):
        data = {"name": client_name}
        print("API Call not implemented yet:")
        print(f"sites/{site_id}/clients/{client_id}", data)
        # return self._post(f"sites/{site_id}/clients/{client_id}", data)

    @staticmethod
    def search_items(items, search_term):
        matching_items = []
        for item in items["data"]:
            if any(
                search_term.lower() in str(value).lower() for value in item.values()
            ):
                matching_items.append(item)
        return matching_items

    @staticmethod
    def find_site_by_name(sites_json, site_name):
        for site in sites_json.get("data", []):
            if site.get("name").lower() == site_name.lower():
                return site
        return None


if __name__ == "__main__":
    # Vars
    secrets_path = "resources/etc/secrets/secrets.yaml"
    unifi_network_api_yaml_path = "resources/etc/collectors/unifi_network_api.yaml"
    secrets = YamlReader(yaml_file=secrets_path)
    unifi_network_api_config = YamlReader(yaml_file=unifi_network_api_yaml_path)

    # Get connection details
    server = unifi_network_api_config.get_value(path="unifi_network_api.server")
    port = unifi_network_api_config.get_value(path="unifi_network_api.port")
    api_key = secrets.get_value(path="secrets.unifi_network_api_token.api_token")

    # logging.debug connection details
    logging.debug(f"API Key: {api_key}")

    unifi_api = UniFiAPI(api_key=api_key, ip=server, port=port)

    try:
        sites = unifi_api.get_sites()
        logging.debug("Sites:", sites)
    except requests.exceptions.RequestException as e:
        logging.debug("Error retrieving sites:", e)
        exit(1)

    site_id = unifi_api.find_site_by_name(sites, "Default")["id"]

    try:
        clients = unifi_api.get_clients(site_id=site_id, limit=2)
        logging.debug("Clients:", clients)
    except requests.exceptions.RequestException as e:
        logging.debug("Error retrieving clients:", e)

    try:
        devices = unifi_api.get_devices(site_id=site_id, limit=5)
        logging.debug("Devices:", devices)
    except requests.exceptions.RequestException as e:
        logging.debug("Error retrieving devices:", e)

    search_term = "Workstation"
    matching_clients = unifi_api.search_items(clients, search_term)
    logging.debug(f"Clients matching '{search_term}':", matching_clients)

    search_term = "UniFi Dream Machine PRO SE"
    matching_devices = unifi_api.search_items(devices, search_term)
    logging.debug(f"Devices matching '{search_term}':", matching_devices)
