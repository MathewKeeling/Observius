from src.modules.snmp.common import get_arp_table
from src.modules.common.secrets import get_secrets_from_file

# Global variables
secrets = get_secrets_from_file("resources/etc/secrets/secrets.csv")
community_string = secrets[6]["password"]

if __name__ == "__main__":
    arp_table = get_arp_table(
        snmp_host="vc-unifi.vcfdom.local", community_string=community_string
    )

    print(arp_table[0])
