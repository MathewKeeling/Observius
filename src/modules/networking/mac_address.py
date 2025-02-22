import subprocess
from src.modules.networking.arp import get_arp_table_linux, get_arp_table_windows
from src.modules.common.secrets import get_secrets_from_file
from netmiko import ConnectHandler


def format_physical_address(hex_string):
    hex_string = hex_string.replace(
        "::", ":"
    )  # Replace double colons with single colons
    physical_address = ":".join(
        hex_string[i : i + 2] for i in range(0, len(hex_string), 2)
    )
    return physical_address


if __name__ == "__main__":
    secrets = get_secrets_from_file("resources/etc/secrets/secrets.csv")
    arp_table_test_linux = get_arp_table_linux(
        remote_host="example-vm-example010.ad.contoso.com",
        username=secrets[3]["username"],
        password=secrets[3]["password"],
    )
    print(arp_table_test_linux[0])
