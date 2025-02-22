import argparse
import csv
import getpass
import os
import subprocess
import sys


def usage():
    print("Usage: {} [UNMANAGE|MANAGE] [options]".format(sys.argv[0]))
    print()
    print("Arguments:")
    print("  UNMANAGE|MANAGE  Whether to unmanage or manage the services")
    print()
    print("Options:")
    print("  -h, --help       Display this help message and exit")
    print("  -s, --services   Comma-separated list of services to unmanage/manage")
    print("  -c, --category   Category of interfaces to unmanage/manage")
    print("  -v, --verbose    Print the command before executing it")


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "status",
    choices=["UNMANAGE", "MANAGE", "unmanage", "manage"],
    nargs="?",
    default=None,
)
parser.add_argument("-h", "--help", action="store_true")
parser.add_argument("-s", "--services")
parser.add_argument("-c", "--category")
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()
if args.help or not args.status:
    usage()
    sys.exit(1)
status = "F" if args.status.upper() == "UNMANAGE" else "A"
services = args.services.upper() if args.services else None
category = args.category
verbose = args.verbose
user = None
password = None
with open("secrets.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        username, password_ = row
        if username == "admin":
            user = username
            password = password_
            break
interfaces = [
    "DNS",
    "FTP",
    "HTTP",
    "HTTPS",
    "ICMP",
    "IMAP",
    "LDAP",
    "NRPE",
    "POP3",
    "SMTP",
    "SNMP",
    "SSH",
    "WS-Man",
    "OpenNMS-JVM",
    "JMX-Minion",
    "JMX-Cassandra",
    "JMX-Cassandra-Newts",
    "MS-RDP",
]
if not services or not category:
    if not services:
        print(
            "Please select the services you want to unmanage/manage (separated by commas):"
        )
        for i, interface in enumerate(interfaces):
            print("[{}] {}".format(i, interface))
        indices = input("Services: ")
        if indices.upper() == "ALL":
            services = ",".join(interfaces)
        else:
            indices = map(int, indices.split(","))
            services = ",".join(interfaces[i] for i in indices)

    if not category:
        category = input("Please enter the category: ")
if services == "ALL":
    services = ",".join(interfaces)
command = 'curl -u {}:{} -X PUT -d "status={}&services={}" "http://localhost:8980/opennms/rest/ifservices?category.name={}"'.format(
    user, password, status, services, category
)
if verbose:
    print("Running command: {}".format(command))
subprocess.run(command, shell=True)
