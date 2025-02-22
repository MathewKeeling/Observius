import nmap


def get_physical_address(ip_address):
    nm = nmap.PortScanner()
    nm.scan(ip_address, arguments="-sP")  # Using -sP instead of -sn

    print("All hosts:", nm.all_hosts())  # Print all scanned hosts for debugging

    if ip_address in nm.all_hosts():
        try:
            physical_address = nm[ip_address]["addresses"]["mac"]
            return physical_address
        except KeyError:
            return None
    else:
        return None


if __name__ == "__main__":
    ip = "127.0.0.1"  # Replace with the target IP address
    mac = get_physical_address(ip)
    if mac:
        print(f"MAC address for {ip} is {mac}")
    else:
        print(f"MAC address for {ip} could not be found")
