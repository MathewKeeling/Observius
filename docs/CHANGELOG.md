# Changelog

## [2025.02.22]

### Added
- Added a table for interfaces in ONI
- OpenNMS API Integration
    - Interfaces.py

### Improved
- Improved OpenNMS Device Import
- Improvements to InterfaceManager
    - Find Interface by MAC
- Improvements to Device.py
    - Specified Manufacturer
    - Specified Mac Address
    - Enhanced Purge Empty Values
- Improvements to DeviceManager
    - Find Device by Name
- Improvements to DeviceTypeManager
    - Find Device Type by slug

## [2025.02.22]

- Improved IPAM Manager
- Improved (and renamed to) ModuleTypeManager
- Created netbox_load

## [2025.02.22]

### Added

- MAC Address Enrichment for ONI
- Module Type Automation
- Device Type Automation
- Lots of Default Devices for automation and inventory management

## [2025.02.22]

### Added

- Inventory Cleaner
    - Able to deduplicate elements in the master_inventory table successfully.
    - Added purge function
- Increased Manufacturer Support
- Increased Device Support
- Improved the IPAM Collector
    - Added IP Range
    - Clarified / improved the IPAM YAML
    - Added a delete function

### Fixes

- DNS Collector


## [2025.02.22]

### Added
- OpenNMS Collector

## [2025.02.22]

### Added
- AD DNS Collector
- SNMP Collector
- Converted several things to OOP
- Added Master Inventory Script
- Fixed trailing [.] in hostnames in the ad dns Collector

### Changed
- Updated `consolidate_data` method in `InventoryManager` class to use a combination of `physical_address` and `ipv4` as the key for consolidation. This ensures that records are correctly identified and merged, even if some records do not have a `physical_address`.

## [2025.02.22]

### Added
- Tests
- ARP Retrieval scripts for Routers via SNMP
- SNMP Scripts using
    - PureSNMP
    - NetMiko
- Libraries
    - networking
    - nmap
    - netmiko
    - observius_identification_system
    - observius_web
    - opennms
        - autodiscovery
        - interfaces
        - nodes
        - requisitions
        - scripts
        - service-management
    - snmp
    - unifi
        - network api capabilities
            - various retrieval mechanisms
            - documentation links
        - unifi controller api capabilities
            - largely just moved them to another repository
            - documentation links
- Updated license notices


## [2025.02.22]

### Added
- Initial release of `observius`.