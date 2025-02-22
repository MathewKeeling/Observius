from src.modules.common.files import csv_to_dict
from src.modules.common.secrets import get_secrets_from_file

import subprocess
import csv


def csv_array(file):
    with open(file, newline="") as csvfile:
        data = list(csv.reader(csvfile))
    return data


def last_octet(ip):
    last_octet = ip.split(".")[-1]
    return last_octet


def add_dns_record(host):
    # Add the DNS Record
    ip = host[0]
    name = host[1]
    base_command = "powershell.exe"
    arguments = f'\
        Add-DnsServerResourceRecordA -Name "{name}" -ZoneName "contoso.com" \
        -AllowUpdateAny -IPv4Address "{ip}" -TimeToLive 01:00:00'
    command = base_command + arguments
    print(command)
    # subprocess.call(command, shell=True)

    # Add the DNS Record
    ip = host[0]
    name = host[1]
    base_command = "powershell.exe"
    arguments = f'\
        Add-DnsServerResourceRecordPtr -Name "{int(last_octet(ip))}" -ZoneName "1.168.192.in-addr.arpa" \
        -AllowUpdateAny -TimeToLive 01:00:00 -AgeRecord -PtrDomainName "{name}.contoso.com"'
    command = base_command + arguments
    print(command)
    # subprocess.call(command, shell=True)


if __name__ == "__main__":
    ip = "https://vc-unifi.vcfdom.local"
    port = "8443"
    site_name = "dwzcm5f1"
    secrets = get_secrets_from_file("resources/etc/secrets/secrets.csv")
    username = secrets[9]["username"]
    password = secrets[9]["password"]
    hosts = csv_array("documentation/unifi/scripts/hosts.csv")
    print(hosts)
    for host in hosts:
        add_dns_record(host)
