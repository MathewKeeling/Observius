#!/bin/bash
# Function to display usage information
usage() {
    echo "Usage: $0 [UNMANAGE|MANAGE] [options]"
    echo
    echo "Arguments:"
    echo "  UNMANAGE|MANAGE  Whether to unmanage or manage the services"
    echo
    echo "Options:"
    echo "  -h, --help       Display this help message and exit"
    echo "  -s, --services   Comma-separated list of services to unmanage/manage"
    echo "  -c, --category   Category of interfaces to unmanage/manage"
    echo "  -v, --verbose    Print the command before executing it"
}
# Check if the first argument is provided
if [[ $# -lt 1 ]]; then
    usage
    exit 1
fi
# Check if the first argument is valid
if [[ $1 != "UNMANAGE" ]] && [[ $1 != "MANAGE" ]] && [[ $1 != "unmanage" ]] && [[ $1 != "manage" ]]; then
    usage
    exit 1
fi
# Set the status based on the first argument
if [[ $1 == "UNMANAGE" ]] || [[ $1 == "unmanage" ]] ; then
    STATUS="F"
else
    STATUS="A"
fi
# Remove the first argument from the list of arguments
shift
VERBOSE=false
# Parse command line options
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -s|--services)
            shift
            SERVICES=${1^^}
            ;;
        -c|--category)
            shift
            CATEGORY=$1
            ;;
        -v|--verbose)
            VERBOSE=true
            ;;
        *)
            break
            ;;
    esac
    shift
done
# Read the secrets.csv file 
while IFS=, read -r username password; do 
    # Check if the username is "admin" 
    if [[ $username == "admin" ]]; then 
        # Store the username and password as variables 
        USER=$username 
        PASSWORD=$password 
        break 
    fi 
done < secrets.csv 
# Possible interfaces:
INTERFACES=(DNS FTP HTTP HTTPS ICMP IMAP LDAP NRPE POP3 SMTP SNMP SSH WS-Man OpenNMS-JVM JMX-Minion JMX-Cassandra JMX-Cassandra-Newts MS-RDP)
# Check if options are provided 
if [[ -z $SERVICES ]] || [[ -z $CATEGORY ]]; then 
    # If no options are provided, display a menu for the user to select services and category 
    # Services selection menu:
    if [[ -z $SERVICES ]]; then 
        echo "Please select the services you want to unmanage/manage (separated by commas):" 
        for i in "${!INTERFACES[@]}"; do 
            printf "[%d] %s\n" $i "${INTERFACES[$i]}" 
        done 
        read -p "Services: " indices 
        if [[ "${indices^^}" == "ALL" ]]; then 
            SERVICES=$(IFS=,; echo "${INTERFACES[*]}")
        else 
            IFS=',' read -ra indices <<< "$indices" 
            SERVICES="" 
            for index in "${indices[@]}"; do 
                SERVICES+="${INTERFACES[$index]},"
            done 
            SERVICES=${SERVICES%?}
        fi 
    fi 
    # Category selection menu:
    if [[ -z $CATEGORY ]]; then 
        read -p "Please enter the category: " CATEGORY 
    fi 
fi 
if [[ "$SERVICES" == "ALL" ]]; then 
   SERVICES=$(IFS=,; echo "${INTERFACES[*]}")
fi 
# Unmanage/manage http on interfaces in category 
# Here is the command:
COMMAND="curl -u $USER:$PASSWORD -X PUT -d \"status=$STATUS&services=${SERVICES}\" \"http://localhost:8980/opennms/rest/ifservices?category.name=$CATEGORY\""
if [[ "$VERBOSE" = true ]]; then 
   echo "Running command: $COMMAND"
fi 
eval $COMMAND
