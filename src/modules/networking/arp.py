from netmiko import ConnectHandler
import subprocess
import winrm


class ArpTable:
    def __init__(self):
        self.entries = []

    def add_entry(self, interface, ip_address, physical_address):
        entry = {
            "interface": interface,
            "ip_address": ip_address,
            "physical_address": physical_address,
        }
        self.entries.append(entry)

    def __str__(self):
        return "\n".join(
            [
                f"Interface: {entry['interface']}, IP Address: {entry['ip_address']}, MAC Address: {entry['physical_address']}"
                for entry in self.entries
            ]
        )


def get_arp_table_linux(remote_host=None, username=None, password=None):
    arp_table = []
    try:
        if remote_host:
            connection = ConnectHandler(
                device_type="linux",
                host=remote_host,
                username=username,
                password=password,
            )
            result = connection.send_command("arp -a")
            connection.disconnect()
        else:
            result = subprocess.check_output(["arp", "-a"]).decode("utf-8")

        lines = result.splitlines()
        for line in lines:
            parts = line.split()
            if len(parts) >= 4:
                entry = {
                    "interface": parts[0],
                    "ip_address": parts[1].strip("()"),
                    "physical_address": parts[3],
                }
                arp_table.append(entry)
    except Exception as e:
        print(f"Error retrieving ARP table: {e}")
    return arp_table


def get_arp_table_windows(remote_host, username, password):
    arp_table = []
    try:
        session = winrm.Session(
            f"http://{remote_host}:5985/wsman", auth=(username, password)
        )
        result = session.run_cmd("arp -a")

        if result.status_code == 0:
            print("Connection successful")
            output = result.std_out.decode("utf-8")
            lines = output.splitlines()
            for line in lines:
                parts = line.split()
                if len(parts) >= 3 and parts[1] == "-":
                    entry = {
                        "interface": parts[0],
                        "ip_address": parts[1],
                        "physical_address": parts[2],
                    }
                    arp_table.append(entry)
        else:
            print(f"Error retrieving ARP table: {result.std_err.decode('utf-8')}")
    except Exception as e:
        print(f"Error retrieving ARP table: {e}")
    return arp_table
