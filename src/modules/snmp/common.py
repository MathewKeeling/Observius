from src.modules.snmp.netmiko_snmpwalk import parse_snmp_output
import subprocess


def get_arp_table(snmp_host: str, community_string: str) -> list:
    """
    Get the ARP table from a network device using SNMP.

    Args:
        snmp_host (str): The IP address or hostname of the device
        community_string (str): The SNMP community string

    Returns:
        list: List of ARP entries from the device
    """
    command = f"snmpwalk -v 2c -c {community_string} {snmp_host} .1.3.6.1.2.1.4.22.1.2"
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return output.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return []


def snmp_walk(snmp_host, community_string, oid) -> list:
    command = f"snmpwalk -v 2c -c {community_string} {snmp_host} {oid}"
    print(f"Executing command: {command}")
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        print(f"Command output: {output}")
        return output.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return []


if __name__ == "__main__":
    snmp_walk(
        snmp_host="core-drt01.ad.contoso.local",
        community_string="community_string",
        oid=".1.3.6.1.2.1.4.22.1.2",
    )
