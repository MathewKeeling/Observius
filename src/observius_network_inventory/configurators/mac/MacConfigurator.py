# More of an enrichment utility...

import csv
import sqlite3
import pandas as pd
from src.modules.sqlite.main import SQLiteManager
import xml.etree.ElementTree as ET


class MacConfigurator:
    def __init__(self, oni_db: SQLiteManager):
        self.db = oni_db
        self.mac_inventory_xml = (
            "src/observius_network_inventory/configurators/mac/resources/vendorMacs.xml"
        )
        self.mac_vendors = self.load_mac_vendors()
        self.original_devices = self.load_original_devices()
        self.updated_devices = self.update_devices_with_vendor()
        self.update_db_with_vendor()

    def load_mac_vendors(self):
        mac_vendors = {}
        tree = ET.parse(self.mac_inventory_xml)
        root = tree.getroot()
        namespace = {"ns": "http://www.cisco.com/server/spt"}
        for vendor in root.findall("ns:VendorMapping", namespace):
            mac_prefix = vendor.get("mac_prefix").strip().upper()
            vendor_name = vendor.get("vendor_name").strip()
            mac_vendors[mac_prefix] = vendor_name
        return mac_vendors

    def lookup_vendor(self, physical_address):
        mac_prefix = physical_address[:8].upper()
        return self.mac_vendors.get(mac_prefix, "Unknown Vendor")

    def load_original_devices(self):
        query = "SELECT * FROM master_inventory"
        result = self.db.execute_sqlite_query(query)
        return pd.DataFrame(result)

    def update_devices_with_vendor(self):
        self.original_devices["vendor"] = self.original_devices[
            "physical_address"
        ].apply(self.lookup_vendor)
        return self.original_devices

    def update_db_with_vendor(self):
        data_list = self.updated_devices.to_dict(orient="records")
        command, values = self.db.build_batch_insert_command(
            "master_inventory", data_list, conflict_resolution="replace"
        )
        self.db.execute_batch_insert(command, values)
