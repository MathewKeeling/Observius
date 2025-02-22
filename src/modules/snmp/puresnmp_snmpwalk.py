import asyncio
from puresnmp import Client, V2C, PyWrapper
from src.modules.common.secrets import get_secrets_from_file


async def snmp_walk():
    client = PyWrapper(Client(snmp_host, V2C(community_string)))
    output = await client.table(oid)
    return output


if __name__ == "__main__":
    # vars
    secrets = get_secrets_from_file("resources/etc/secrets/secrets.csv")
    community_string = secrets[6]["password"]
    username = secrets[3]["username"]
    password = secrets[3]["password"]
    snmp_host = "127.0.0.1"
    oid = ".1.3.6.1.2.1.4.22.1.2"

    # run the snmp walk
    results = asyncio.run(snmp_walk())

    # print the results
    print(results)
