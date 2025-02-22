# API Documentation: https://ubntwiki.com/products/software/unifi-controller/api
# Sample Code: https://github.com/DataKnox/CodeSamples/blob/master/Python/Networking/Ubiquiti/ubnt.py
import csv
import json
import requests
import urllib3

from src.modules.common.files import csv_to_dict
from src.modules.common.secrets import get_secrets_from_file


def array_to_csv(array, file_name="output.csv"):
    """
    Converts an array to a CSV file.

    Args:
        array (list): List of strings, where each string is a row of comma-separated values.
        file_name (str): Name of the output CSV file. Defaults to "output.csv".
    """
    with open(file_name, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        for row in array:
            writer.writerow(row.split(","))


def get_clients(session, ip: str, port: int, site_name: str):
    """
    Retrieves a list of clients connected to the network.

    Args:
        session (requests.Session): The session object for making requests.
        ip (str): IP address of the gateway.
        port (int): Port number of the gateway.
        site_name (str): Name of the site.

    Returns:
        list: List of dictionaries with client details.
    """
    gateway = {"ip": f"{ip}", "port": f"{port}"}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    getClientsUrl = f"api/s/{site_name}/stat/sta"
    url = f"https://{gateway['ip']}:{gateway['port']}/{getClientsUrl}"
    response = session.get(url, headers=headers, verify=False)
    api_data = response.json()

    responseList = api_data.get("data", [])
    if not responseList:
        print("No clients found.")
        return []

    clients = []
    for client in responseList:
        client_info = {
            "ipv4": client.get("last_ip"),
            "physical_address": client.get("mac"),
            "hostname": client.get("hostname"),
            "ipv6": client.get("ipv6", None),  # Assuming 'ipv6' key might be present
            "first_seen": client.get("first_seen"),
            "last_seen": client.get("last_seen"),
        }
        clients.append(client_info)

    return clients


def get_devices(session, ip: str, port: int, site_name: str):
    """
    Retrieves a list of devices connected to the network.

    Args:
        session (requests.Session): The session object for making requests.
        ip (str): IP address of the gateway.
        port (str): Port number of the gateway.

    Returns:
        list: List of devices with their details such as name, IP, MAC address, DHCP type, state, and upgradable status.
    """
    gateway = {"ip": f"{ip}", "port": f"{port}"}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    getDevicesUrl = f"api/s/{site_name}/stat/device"
    url = f"https://{gateway['ip']}:{gateway['port']}/{getDevicesUrl}"
    response = session.get(url, headers=headers, verify=False)
    api_data = response.json()

    responseList = api_data.get("data", [])
    devices_info = []
    for device in responseList:
        device_info = {
            "name": device.get("name"),
            "ip": device.get("ip"),
            "mac": device.get("mac"),
            "dhcp": device.get("config_network", {}).get("type"),
            "state": "online" if device.get("state") == 1 else "offline",
            "upgradable": device.get("upgradable"),
        }
        devices_info.append(device_info)

    return devices_info


def get_session(ip, port, user, password):
    """
    Establishes a session with the gateway.

    Args:
        ip (str): IP address of the gateway.
        port (str): Port number of the gateway.
        user (str): Username for authentication.
        password (str): Password for authentication.

    Returns:
        requests.Session: The session object for making requests.
    """
    # This is for the old version of the Unifi API
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # set up connection parameters in a dictionary
    gateway = {"ip": f"{ip}", "port": f"{port}"}
    # set REST API headers
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    # set URL parameters
    loginUrl = "api/login"
    url = f"https://{gateway['ip']}:{gateway['port']}/{loginUrl}"
    # set username and password
    body = {"username": f"{user}", "password": f"{password}"}
    # Open a session for capturing cookies
    session = requests.Session()
    # login
    response = session.post(url, headers=headers, data=json.dumps(body), verify=False)
    # parse response data into a Python object
    api_data = response.json()

    return session


def get_site_name_from_csv(csv_file):
    """
    Retrieves the site name from a CSV file.

    Args:
        csv_file (str): Path to the CSV file.

    Returns:
        str: The site name.
    """
    with open(csv_file, "r") as f:
        for line in f:
            site_name = line.strip()
    return site_name


def get_sites(session, ip, port):
    """
    Retrieves a list of sites.

    Args:
        session (requests.Session): The session object for making requests.
        ip (str): IP address of the gateway.
        port (str): Port number of the gateway.

    Returns:
        list: List of site names.
    """
    gateway = {"ip": f"{ip}", "port": f"{port}"}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    getSitesUrl = "api/self/sites"
    url = f"https://{gateway['ip']}:{gateway['port']}/{getSitesUrl}"
    response = session.get(url, headers=headers, verify=False)
    api_data = response.json()

    responseList = api_data.get("data", [])
    sites = []
    for site in responseList:
        sites.append(site["name"])
    return sites


if __name__ == "__main__":
    ip = "127.0.0.1"
    port = "8443"
    site_name = "dwzcm5f1"
    secrets = get_secrets_from_file("resources/etc/secrets/secrets.csv")
    username = secrets[4]["username"]
    password = secrets[4]["password"]
    session = get_session(ip, port, username, password)

    clients = get_clients(session, ip, port, site_name=site_name)
    devices = get_devices(session=session, ip=ip, port=port, site_name=site_name)
    sites = get_sites(session=session, ip=ip, port=port)
    # print(devices)
    # print(clients)
    print(sites)
