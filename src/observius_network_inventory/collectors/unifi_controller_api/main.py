import time
import logging
from src.modules.common.secrets import get_secrets_from_file
from src.modules.unifi.unifi_controller_api.main import (
    get_session,
    get_clients,
    get_devices,
)
from src.modules.yaml.YamlReader import YamlReader
from src.modules.sqlite.main import SQLiteManager
from src.modules.common.LoggerSetup import LoggerSetup


def current_epoch_time():
    return int(time.time())


def query_unifi_sites() -> list:
    unifi_yaml_path = "resources/etc/collectors/unifi_controller_api.yaml"
    unifi_yaml = YamlReader(unifi_yaml_path)
    sites = unifi_yaml.get_section("unifi_controller_sites")
    unifi_results_list = []

    try:
        secrets = get_secrets_from_file("resources/etc/secrets/secrets.csv")
        ip = "127.0.0.1"
        port = 8443
        username = secrets[4]["username"]
        password = secrets[4]["password"]
        session = get_session(ip, port, username, password)

        for site in sites:
            clients = get_clients(session=session, ip=ip, port=port, site_name=site)
            devices = get_devices(session=session, ip=ip, port=port, site_name=site)
            site_data = {"site": site, "clients": clients, "devices": devices}
            unifi_results_list.append(site_data)

            # Debug statements to capture the data
            logging.debug(f"Site: {site}")
            logging.debug(f"Clients: {clients}")
            logging.debug(f"Devices: {devices}")

    except Exception as e:
        logging.error(f"Error querying UniFi sites: {e}")

    return unifi_results_list


def unifi_collection(oni_db: SQLiteManager):
    unifi_source_results = query_unifi_sites()
    for source_result in unifi_source_results:
        for client in source_result["clients"]:
            ipv4 = client.get("ipv4")
            physical_address = client.get("physical_address")
            HOSTNAME = ""  # hostname data is not reliable, disabled for now"
            ipv6 = client.get("ipv6")
            first_seen = client.get("first_seen")
            last_seen = client.get("last_seen")

            # Check if the client already exists in the database
            query = "SELECT COUNT(*) FROM source_unifi_controller_api WHERE ipv4 = ?"
            result = oni_db.execute_sqlite_command(query, (ipv4,))
            count = result[0][0]

            if count > 0:
                # Update the last_seen time
                update_query = """
                    UPDATE source_unifi_controller_api
                    SET last_seen = ?
                    WHERE ipv4 = ?
                """
                oni_db.execute_sqlite_command(
                    update_query, (current_epoch_time(), ipv4)
                )
            else:
                # Set the first_seen and last_seen times
                client_dict = {
                    "ipv4": ipv4,
                    "physical_address": physical_address,
                    "HOSTNAME": "",  # hostname data is not reliable, disabled for now
                    "ipv6": ipv6,
                    "first_seen": first_seen,
                    "last_seen": last_seen,
                }
                unifi_source_insert_query = oni_db.build_insert_command(
                    table_name="source_unifi_controller_api", data=client_dict
                )
                oni_db.execute_sqlite_command(
                    unifi_source_insert_query[0], unifi_source_insert_query[1]
                )

        for device in source_result["devices"]:
            physical_address = device.get("mac")
            if physical_address:
                # Map the device data to the database schema
                device_dict = {
                    "ipv4": device.get("ip"),
                    "HOSTNAME": "",  # hostname data is not reliable, disabled for now
                    "physical_address": physical_address,
                    "first_seen": current_epoch_time(),
                    "last_seen": current_epoch_time(),
                }

                # Check if the device already exists in the database
                query = "SELECT COUNT(*) FROM source_unifi_controller_api WHERE physical_address = ?"
                result = oni_db.execute_sqlite_command(query, (physical_address,))
                count = result[0][0]

                if count > 0:
                    # Update the last_seen time
                    update_query = """
                        UPDATE source_unifi_controller_api
                        SET last_seen = ?
                        WHERE physical_address = ?
                    """
                    oni_db.execute_sqlite_command(
                        update_query, (current_epoch_time(), physical_address)
                    )
                else:
                    # Insert the new device data
                    unifi_source_insert_query = oni_db.build_insert_command(
                        table_name="source_unifi_controller_api", data=device_dict
                    )
                    oni_db.execute_sqlite_command(
                        unifi_source_insert_query[0], unifi_source_insert_query[1]
                    )
            else:
                logging.error("MAC address not found in device data")


if __name__ == "__main__":
    oni_yaml_file = "resources/etc/oni/oni.yaml"
    oni_db_yaml_file = "resources/etc/databases/oni.yaml"
    oni_yaml = YamlReader(yaml_file=oni_yaml_file)
    oni_db_yaml = YamlReader(yaml_file=oni_db_yaml_file)
    db = SQLiteManager(database_path="resources/db/oni.db")

    # Variable Initialization
    program_name = oni_yaml.get_value("oni.settings.program_name")
    logging_level = oni_yaml.get_value("oni.settings.log_level")
    logging_path = oni_yaml.get_value("oni.settings.log_file_path")
    logger = LoggerSetup(
        name=program_name, log_file=logging_path, level=logging_level
    ).get_logger()
    unifi_collection(oni_db=db)
