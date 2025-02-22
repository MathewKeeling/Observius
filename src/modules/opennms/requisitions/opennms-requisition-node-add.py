import requests
import time
import base64


# Services look like this:
# <monitored-service service-name="ActiveMQ"/>
# Make a method that takes a list of services and returns the XML strings in a list


def add_nodes(
    auth=str,
    basename=str,
    location=str,
    nodes=list,
    requisition=str,
    services=str,
    debug=False,
) -> None:
    """
    Adds nodes to the OpenNMS server.

    Args:
        auth (str): The authorization token.
        basename (str): The base name for the nodes.
        location (str): The location of the nodes.
        nodes (list): A list of dictionaries representing the nodes to be added.
        requistion (str): The requisition for the nodes.
        services (str): The services to be added to the nodes.
        url (str): The URL of the OpenNMS server.

    Returns:
        None
    """

    url = f"http://{basename}:8980/opennms/rest/requisitions/{requisition}/nodes"
    foreign_id = get_epoch_time_ms()
    for node in nodes:

        # Skip nodes without an FQDN
        if node["FQDN"] == "":
            continue

        headers = {
            "Authorization": auth,
            "Content-Type": "application/xml",
        }
        data = f"""
            <node location="{node["MinionLocation"]}" foreign-id="{foreign_id}" node-label="{node["FQDN"]}">
                <interface ip-addr="{node["IP"]}" snmp-primary="P">
                {services}
                </interface>
            </node>
            """
        response = requests.post(url, headers=headers, data=data)

        if debug:
            print(headers)
            print(data)

        if response.status_code != 202:
            if debug:
                print(response.status_code)
                print(response.text)
            print(f"Node {node['FQDN']} not added to requisition {requisition}.")
            return
        else:
            print(f"Node {node['FQDN']} added to requisition {requisition}.")


def csv_to_dict(file: str) -> list:
    """
    Converts a CSV file with headers in utf-8 format to a list of dictionaries.

    Args:
        file (str): The path to the CSV file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row in the CSV file.
    """
    with open(file, "r", encoding="utf-8-sig") as f:
        data = f.read().split("\n")
        headers = data[0].split(",")
        data = data[1:]
        data = [x.split(",") for x in data]
        data = [dict(zip(headers, x)) for x in data if x != [""]]
        return data


def get_epoch_time_ms() -> int:
    """
    Returns the current time in milliseconds since the epoch.
    """
    return int(time.time() * 1000)


def get_services(services: list) -> str:
    """
    Returns the XML strings for the services to be added to the nodes.

    Args:
        services (list): A list of services to be added to the nodes.

    Returns:
        str: A string representing the XML strings for the services to be added to the nodes.
    """
    services = "\n".join(
        [f'<monitored-service service-name="{service}"/>' for service in services]
    )
    return services


if __name__ == "__main__":
    admin_user = "admin"
    admin_pass = "admin"
    requisition = "kcltd-core"
    url_fqdn = "opennms.ad.contoso.com"
    BASIC_AUTH_TOKEN = (
        f"Basic {base64.b64encode(f'{admin_user}:{admin_pass}'.encode()).decode()}"
    )
    print('"', BASIC_AUTH_TOKEN, '"')

    # Generate CSV of Dictionaries
    nodes_path = "./servers/opennms/installer/script/api/nodes.csv"

    services = ["ICMP", "SNMP"]

    # Add Nodes
    nodes_to_add = csv_to_dict(nodes_path)

    print("Nodes to add: ", len(nodes_to_add))

    for node in nodes_to_add:
        add_nodes(
            auth=BASIC_AUTH_TOKEN,
            basename=url_fqdn,
            nodes=nodes_to_add,
            requisition=requisition,
            services=get_services(services),
        )
