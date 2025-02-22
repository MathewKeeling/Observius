import requests
import json
import datetime
import time
import pandas as pd


def onms_get_all_nodes(server: str, username: str, password: str):
    # OpenNMS details
    # url = "http://opennms.contoso.local:8980/opennms/api/v2/nodes?limit=0"
    url = f"http://{server}/opennms/api/v2/nodes?limit=0"
    # Send GET request to OpenNMS API
    response = requests.get(
        url, auth=(username, password), headers={"Accept": "application/json"}
    )
    results = {}
    # Check if request was successful
    if response.status_code == 200:
        results = response.json()
    return results


def onms_delete_requisition_device_by_foreignSource_and_foreignId(
    foreignSource, foreignId
):
    # Delete requisition
    # curl -X DELETE "http://opennms.contoso.local:8980/opennms/rest/requisitions/foreignSource/nodes/foreignId"
    url = f"http://{server}/opennms/rest/requisitions/{foreignSource}/nodes/{foreignId}"
    response = requests.delete(url, headers=headers, auth=(username, password))
    result = ""
    if response.status_code == 202:
        result = response.text
    return result


def omns_device_delete_by_id(Id):
    # Delete Data from database
    # Using DELETE /nodes/{id}
    url = f"http://{server}/opennms/rest/nodes/{Id}"
    response = requests.delete(url, headers=headers, auth=(username, password))
    result = ""
    if response.status_code == 202:
        # Delete Data from database
        # Using foreign source and foreign ID: DELETE /nodes/foreignSource:foreignId
        result = response.text
    return result


def onms_get_ipinterfaces_for_id(server: str, username: str, password: str, id: str):
    # API endpoint
    url = f"http://{server}/opennms/api/v2/nodes/{id}/ipinterfaces"
    # Headers
    headers = {"Content-Type": "application/json"}
    # Send the GET request to get the ipinterface table for a device
    response = requests.get(url, headers=headers, auth=(username, password))
    result = {}  # Initialize result to an empty dictionary
    if response.status_code == 200:
        result = json.loads(response.text)
    return result


def onms_get_primary_ip_for_id(server: str, username: str, password: str, id: str):
    ipinterfaces = onms_get_ipinterfaces_for_id(
        server=server, username=username, password=password, id=id
    )
    primaryip = ""
    for interfaces in ipinterfaces["ipInterface"]:
        # "snmpPrimary": "P",
        if interfaces["snmpPrimary"] == "P":
            primaryip = interfaces["ipAddress"]
    return primaryip


def epoch_time():
    return round(time.time() * 1000)
