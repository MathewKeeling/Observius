import nmap


def scan_subnet(subnet: str, verbose=False, interface=None, ping_timeout=1000):
    """
    Perform a rootless Nmap scan on a subnet and record which IP addresses reply.

    Args:
        subnet (str): The subnet to scan in CIDR notation.
        verbose (bool): If True, print status messages.
        interface (str): The network interface to use for the scan.
        ping_timeout (int): The timeout for the ping scan in milliseconds.

    Returns:
        list: A list of IP addresses that responded to the ping scan.
    """
    nm = nmap.PortScanner()
    if verbose:
        print(f"Scanning subnet: {subnet}")

    try:
        arguments = f"-sn --host-timeout {ping_timeout}ms"  # Ping scan with timeout
        if interface:
            arguments += f" -e {interface}"
        nm.scan(hosts=subnet, arguments=arguments)
    except Exception as e:
        print(f"Error scanning subnet: {e}")
        return []

    responding_hosts = [host for host in nm.all_hosts()]
    if verbose:
        for host in responding_hosts:
            print(f"Found host: {host}")

    return responding_hosts


def scan_host_details(host: str, verbose=False):
    """
    Perform a detailed service scan on a single host.

    Args:
        host (str): The IP address of the host to scan.
        verbose (bool): If True, print status messages.

    Returns:
        dict: A dictionary containing detailed information about the host.
    """
    nm = nmap.PortScanner()
    if verbose:
        print(f"Scanning host: {host}")

    try:
        nm.scan(
            hosts=host, arguments="-sV -F --min-parallelism 10 --max-parallelism 100"
        )
        host_info = {
            "ip": nm[host]["addresses"].get("ipv4", "N/A"),
            "mac": nm[host]["addresses"].get("mac", "N/A"),
            "hostname": nm[host].hostname(),
            "state": nm[host].state(),
            "services": [],
        }
        for proto in nm[host].all_protocols():
            ports = nm[host][proto].keys()
            for port in ports:
                service_info = {
                    "port": port,
                    "protocol": proto,
                    "name": nm[host][proto][port]["name"],
                    "state": nm[host][proto][port]["state"],
                }
                host_info["services"].append(service_info)
        if verbose:
            print(f"Detailed info for host {host}: {host_info}")
        return host_info
    except Exception as e:
        if verbose:
            print(f"Error scanning services for {host}: {e}")
        return {}


if __name__ == "__main__":
    subnet = "127.0.0.1/24"
    responding_hosts = scan_subnet(subnet=subnet, verbose=True, ping_timeout=6000)
    # detailed_scan_results = [scan_host_details(host, verbose=True) for host in responding_hosts]
    # print(detailed_scan_results)
