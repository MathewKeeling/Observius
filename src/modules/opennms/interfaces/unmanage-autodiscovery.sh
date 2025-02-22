#!/bin/bash

# Author: Mathew Keeling
# 
# Date: 22 February 2025

# Change to the working Directory
cd /opt/installdir/automation/

# Read the secrets.csv file
while IFS=, read -r username password
do
    # Check if the username is "admin"
    if [[ $username == "admin" ]]
    then
        # Store the username and password as variables
        USER=$username
        PASSWORD=$password
        break
    fi
done < secrets.csv

# Force Unmanage Devices in the Autodiscovery Requisition--by Force Unmanaging Devices with 'Autodiscovery' Tag
curl -u $USER:$PASSWORD -X PUT -d "status=F&services=DNS,FTP,HTTP,HTTPS,ICMP,IMAP,LDAP,NRPE,POP3,SMTP,SNMP,SSH,WS-Man,OpenNMS-JVM,JMX-Minion,JMX-Cassandra,JMX-Cassandra-Newts,MS-RDP" "http://localhost:8980/opennms/rest/ifservices?category.name=Autodiscovery"
