from src.modules.snmp.netmiko_snmpwalk import parse_snmp_output
from src.modules.snmp.common import get_arp_table
from src.modules.yaml.YamlReader import YamlReader
from src.modules.sqlite.main import SQLiteManager
import time
import logging


def current_epoch_time():
    return int(time.time())


def query_snmp_hosts() -> list:
    snmp_yaml_path = "resources/etc/collectors/snmp.yaml"
    snmp_yaml = YamlReader(snmp_yaml_path)
    groups = []
    snmp_results_list = []
    for key in snmp_yaml.get_section("snmp_hosts"):
        groups.append(key.upper())

    for group in groups:
        group_data = snmp_yaml.get_section(f"snmp_hosts.{group.lower()}")
        if group_data is None:
            continue
        for host_index in range(len(group_data)):
            snmp_host = group_data[host_index]["ip_address"].upper()
            community_string = group_data[host_index]["community_string"]
            oid = group_data[host_index]["arp_oid"]
            snmp_output = get_arp_table(
                snmp_host=snmp_host, community_string=community_string
            )
            arp_table_dict = parse_snmp_output(snmp_output=snmp_output)
            snmp_results_list.append(arp_table_dict)
    return snmp_results_list


def snmp_collection(oni_db: SQLiteManager):
    snmp_source_results = query_snmp_hosts()
    for source_result in snmp_source_results:
        for arp_table_dict in source_result:
            physical_address = arp_table_dict.get("physical_address").upper()
            if physical_address:
                query = "SELECT COUNT(*) FROM source_snmp WHERE physical_address = ?"
                result = oni_db.execute_sqlite_command(query, (physical_address,))
                count = result[0][0]

                if count > 0:
                    update_query = """
                        UPDATE source_snmp
                        SET last_seen = ?
                        WHERE physical_address = ?
                    """
                    oni_db.execute_sqlite_command(
                        update_query, (current_epoch_time(), physical_address)
                    )
                else:
                    arp_table_dict["first_seen"] = current_epoch_time()
                    arp_table_dict["last_seen"] = current_epoch_time()
                    snmp_source_insert_query = oni_db.build_insert_command(
                        table_name="source_snmp", data=arp_table_dict
                    )
                    oni_db.execute_sqlite_command(
                        snmp_source_insert_query[0], snmp_source_insert_query[1]
                    )
            else:
                logging.error("MAC address not found in arp_table_dict")


if __name__ == "__main__":
    oni_db = SQLiteManager(database_path="resources/db/oni.db")
    snmp_collection(oni_db=oni_db)
    print("SNMP Collection Complete")
    print()
