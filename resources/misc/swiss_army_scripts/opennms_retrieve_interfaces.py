from src.modules.common.json import json_to_file
from src.modules.networking.mac_address import format_physical_address
from src.modules.opennms.nodes.common import (
    onms_get_all_nodes,
    onms_get_ipinterfaces_for_id,
    onms_get_primary_ip_for_id,
)

if __name__ == "__main__":
    print("Hello World!")

    test_id = "4"

    nodes_test = onms_get_all_nodes(
        server="example-vm-example004.ad.contoso.com", username="admin", password="admin"
    )

    interfaces_test = onms_get_ipinterfaces_for_id(
        server="example-vm-example004.ad.contoso.com",
        username="admin",
        password="admin",
        id=test_id,
    )

    primary_ip_test = onms_get_primary_ip_for_id(
        server="example-vm-example004.ad.contoso.com",
        username="admin",
        password="admin",
        id=test_id,
    )

    print(nodes_test)

    # json_to_file(nodes_test, "./resources/workspace/observius/nodes_test.json")
    # json_to_file(
    #     interfaces_test, "./resources/workspace/observius/interfaces_test.json"
    # )
#
# test_mac_unformatted = interfaces_test["ipInterface"][0]["snmpInterface"][
#     "physAddr"
# ]
# test_mac = format_physical_address(hex_string=test_mac_unformatted)
# print(test_mac)
