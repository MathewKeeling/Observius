# ONI Databases

## Inventory Posture

### tables

#### 'INTERFACE'

    Purpose:
        Stores all interfaces
    Unique Constraints:
        Primary Key:
            physical_address
        <>
    Columns:
        ifType
        ifSpeed
        mgmtIp
        ipv4
        ipv6
        hostname
        physical_address <UNIQUE KEY>

#### 'NETBOX_SEED' (formerly 'MASTER_INVENTORY')

    Purpose:
        Staging area for 'NETBOX_DEVICE's
    Unique Constraints:
        Primary Key:
            Hostname
        <>
    Columns:
        Hostname <UNIQUE KEY>
        Manufacturer
        Model
        Last Seen
        First Seen

        

#### 

## Overview

1. [ONI MAIN]
    1. CREATES 'ONI_DB'
    1. STARTS COLLECTORS
    1. BUILDS 'MASTER_INVENTORY' table
        1. -> change to
            1. BUILD INTERFACE table
            1. BUILD NETBOX_SEED table
    1. CLEANS 'MASTER_INVENTORY' table
    1. ENRICHES 'MASTER_INVENTORY' table
        1. MAC address manufacturer lookup

1. [NETBOX_LOAD]
    1. GET 'ONI_DEVICES' from 'ONI_DB' 'NETBOX_SEED'
    1. 