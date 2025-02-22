import requests
import json
import datetime
import time
import pandas as pd


def get_all_ip_interfaces(server: str, username: str, password: str):
    # API endpoint
    url = f"http://{server}/opennms/api/v2/ipinterfaces"
    # Headers
    headers = {"Content-Type": "application/json"}
    # Send the GET request to get the interface table
    response = requests.get(url, headers=headers, auth=(username, password))
    result = {}  # Initialize result to an empty dictionary
    if response.status_code == 200:
        result = json.loads(response.text)
    return result


def get_all_snmp_interfaces(server: str, username: str, password: str):
    # API endpoint
    url = f"http://{server}/opennms/api/v2/snmpinterfaces"
    # Headers
    headers = {"Content-Type": "application/json"}
    # Send the GET request to get the interface table
    response = requests.get(url, headers=headers, auth=(username, password))
    result = {}  # Initialize result to an empty dictionary
    if response.status_code == 200:
        result = json.loads(response.text)
    return result
