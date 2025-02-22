#


```


```

## MUNGING 'IP' 'MAC' 'HOSTNAME

20250215 NEEDS FIXED

    Example:
        Example Device:
            example-vm-example014.AD.contoso.local
            127.0.0.1
            00:50:56:8B:D7:4C
        Problem:
            Does not Appear in Netbox
            Does not appear in 'MASTER_INVENTORY' table in 'ONI_DB'

## Determining Management 'INTERFACE' (VERSION 1)

1. 'INTERFACE' where 'INTERFACE_IP' matches Hostname in DNS
1. 'INTERFACE' where 'sysName' 
1. 'INTERFACE' where 'ifType' is 'lo' && 'INTERFACE_IP' reachable via PING
1. 'INTERFACE' where index is lowest 


## Netbox

1. Bring in 'ONI_DEVICE' with 'ROLE': 'AUTODISCOVERED'
    1. When the device is in netbox, the user has NO privileges to edit 'AUTODISCOVERED' devices.
1. Add a button to the 'AUTODISCOVERED' devices
    1. Button 'APPLY_DEVICE_ROLE'


### 'APPLY_DEVICE_ROLE' (VERSION 2)

#### User Story

1. Provide a list of 'DEVICE_TYPES'
1. Pick a 'DEVICE_TYPE'
1. The 'AUTODISCOVERED' device is deleted.
1. A new 'NETBOX_DEVICE' with proper 'DEVICE_TYPE' is created.

#### Implementation

    1. ELIMINATE SNMP Collection from OpenNMS Temporarily
        1. Until a disambiguation method is estbalished for SNMP interfaces
    1. Don't record any interfaces from opennms unless it is 'PRIMARY_IP'

1. GET data from current 'NETBOX_DEVICE' (X)
    1. Capture the MAC address of the 'PRIMARY_IP'
1. GET data from the ONI_DB with any information already known about the 'NETBOX_DEVICE'
1. DELETE 'NETBOX_DEVICE'
    1. IF 'INTERFACES' are not automatically deleted
        1. Delete 'INTERFACES' from 'NETBOX_DEVICE'
1. POST a new 'NETBOX_DEVICE' with properly selected 'DEVICE_TYPE'
1. PUT 'EXISTING INFORMATION' against 'NETBOX_DEVICE'

    'ONI_DEVICE'
        IF SNMP_ACCESS
            <KNOWN_IF_NAME>
            <KNOWN_IF_NAME>
        ELSE (FLAT)
            <UNKNOWN_IF_NAME> <MANAGEMENT_IP>

1. PUT IP ADDRESSES