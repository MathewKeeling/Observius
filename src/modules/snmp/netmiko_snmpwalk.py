import re
from src.modules.netmiko.connection import run_commands_on_host
from src.modules.common.secrets import get_secrets_from_file

# Global variables
secrets = get_secrets_from_file("resources/etc/secrets/secrets.csv")

# Credentials to the server hosting automation tools
username = secrets[3]["username"]
password = secrets[3]["password"]


def parse_snmp_output(snmp_output):
    # Regular expression to match the required pattern
    pattern = re.compile(
        r"iso(?:\.\d+)+\.(\d+)\.(\d+\.\d+\.\d+\.\d+)\s+=\s+Hex-STRING:\s+([0-9A-F]{2}(?:\s[0-9A-F]{2}){5})"
    )

    # Generate the list of dictionaries
    result = []
    for line in snmp_output:
        if line.strip():  # Check if the line is not blank
            match = pattern.search(line)
            if match:
                interface, ip, mac_hex = match.groups()
                mac = ":".join(mac_hex.split())
                result.append(
                    {
                        "physical_address": mac,
                        "ipv4": ip,
                        "interface_name": "",
                        "hostname": "",
                    }
                )

    return result


def snmp_walk(snmp_host, community_string, oid) -> list:
    command = f"snmpwalk -v 2c -c {community_string} {snmp_host} {oid}"
    print(f"Executing command: {command}")
    output = run_commands_on_host(
        host=snmp_host,
        username=username,
        password=password,
        device_type="linux",
        commands=[command],
    )
    print(f"Command output: {output}")
    return output


if __name__ == "__main__":
    snmp_walk(
        snmp_host="core-drt01.ad.contoso.local",
        community_string="community_string",
        oid=".1.3.6.1.2.1.4.22.1.2",
    )
