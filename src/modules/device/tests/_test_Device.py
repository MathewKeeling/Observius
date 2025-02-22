from src.modules.device.Device import Device


def main():
    device_data = {
        "ipv4": "127.0.0.1",
        "mac": "00:1A:2B:3C:4D:5E",
        "serial_number": "SN123456",
        "manufacturer": "DeviceCorp",
        "dns_name": "device1.local",
        "metadata": {"location": "Data Center 1"},
        "location": "Default",
        "categories": [],
        "foreignSource": "selfmonitor",
        "assetRecord": {
            "category": "Unspecified",
            "password": None,
            "port": None,
            "id": "2",  # Changed to string
            "operatingSystem": None,
            "description": None,
            "username": None,
            "vendor": None,
            "modelNumber": None,
            "manufacturer": None,
            "serialNumber": None,
            "circuitId": None,
            "assetNumber": None,
            "rack": None,
            "slot": None,
            "division": None,
            "department": None,
            "building": "selfmonitor",
            "floor": None,
        },
        "foreignId": "1",
        "first_seen": 1726383030318,
        "lastIngressFlow": None,
        "lastEgressFlow": None,
        "labelSource": "U",
        "last_seen": 1735517642872,
        "type": "A",
        "id": "1",
    }

    device = Device(**device_data)
    print(device)


if __name__ == "__main__":
    main()
