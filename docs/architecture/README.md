# 

## Overview of Product Features

- **Automated Network Discovery**: Seamlessly discover and inventory network devices using multiple collectors such as DNS, SNMP, ARP, DHCP, and more.
- **Centralized Configuration**: Manage all configuration settings through a single YAML-based configuration file, simplifying setup and maintenance.
- **Robust Logging**: Integrated logging system to track and monitor the status of network discovery and data collection processes.
- **Extensible Architecture**: Easily add new collectors and extend the functionality of ONI to meet specific network management needs.
- **SQLite Database**: Store and manage network inventory data in a lightweight and efficient SQLite database.

- DDI (DNS, DHCP, IPAM)
  - DNS
    - Dump DNS records
  - DHCP
    - Dump DHCP logs
  - IPAM
    - Populate Netbox with Host Information
      - Add host
      - Remove Host
      - Modify Host
    - Netbox Monitoring Configuration
      - Set Device/interface
        - Monitored
        - Unmonitored
        - Decommissioned
        - Retired
        - Maintenance
- Network Monitoring System Collector
  - OpenNMS
    - Autodiscovery
      - Populate Autodiscovery
      - Run Autodiscovery
    - Requisition Management
      - Create Requisitions
      - Delete Requisitions
    - Metadata Harvesting
      - Obtain Node Information
        - IPv4
        - Hostname
        - SNMP
          - Interface Information
    - Node Management
      - Create Nodes
      - Modify Nodes
      - Delete Nodes