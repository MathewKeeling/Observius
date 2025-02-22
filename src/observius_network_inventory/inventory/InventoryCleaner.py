import sqlite3
from src.modules.yaml.YamlReader import YamlReader
import logging
import sqlite3
import logging


class InventoryCleaner:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.purge_criteria = ["ipv4", "physical_address", "hostname"]
        self.clean_inventory(filters=["ipv4"])
        self.clean_inventory(filters=["physical_address"])
        self.purge_empty_rows()
        self.close_connection()

    def clean_inventory(self, filters=None):
        while True:
            rows = self.get_duplicate_rows(filters=filters)
            if not rows:
                break
            self.merge_and_delete(rows)

    def get_duplicate_rows(self, filters=None):
        if filters:
            print(f"Filtering by '{filters}'")
        join_condition = " AND ".join([f"t1.{col} = t2.{col}" for col in filters])
        self.cursor.execute(
            f"""
            SELECT t1.id, t1.ipv4, t1.ipv6, t1.hostname, t1.physical_address, t1.interface_name, t1.guid_hash, t1.description, t1.device_type, t1.vendor, t1.first_seen, t1.last_seen,
                   t2.id, t2.ipv4, t2.ipv6, t2.hostname, t2.physical_address, t2.interface_name, t2.guid_hash, t2.description, t2.device_type, t2.vendor, t2.first_seen, t2.last_seen
            FROM master_inventory t1
            JOIN master_inventory t2 ON {join_condition} AND t1.id < t2.id
            LIMIT 1
            """
        )
        return self.cursor.fetchone()

    def merge_and_delete(self, row):
        n_id, n_data, m_id, m_data = row[0], row[1:12], row[12], row[13:24]

        # Determine which row has the latest 'last_seen' date
        latest_data = n_data if row[11] > row[23] else m_data
        other_data = m_data if row[11] > row[23] else n_data

        # Merge data, prioritizing non-empty values from the latest row
        merged_data = [
            latest_value if latest_value not in (None, "") else other_value
            for latest_value, other_value in zip(latest_data, other_data)
        ]

        merged_data[9] = min(n_data[9], m_data[9])  # Use the earliest 'first_seen' date

        # Update the database with the merged data
        self.cursor.execute(
            """
            UPDATE master_inventory
            SET ipv4 = ?, ipv6 = ?, hostname = ?, physical_address = ?, interface_name = ?, guid_hash = ?, description = ?, device_type = ?, vendor = ?, first_seen = ?, last_seen = ?, source = 'synthetic'
            WHERE id = ?
            """,
            (*merged_data, n_id),
        )
        self.conn.commit()

        # Delete the second row
        self.cursor.execute("DELETE FROM master_inventory WHERE id = ?", (m_id,))
        self.conn.commit()

    def purge_empty_rows(self):
        conditions = " OR ".join(
            [f"{col} IS NULL OR {col} = ''" for col in self.purge_criteria]
        )
        self.cursor.execute(f"DELETE FROM master_inventory WHERE {conditions}")
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


if __name__ == "__main__":
    oni_db_yaml_file = "resources/etc/databases/oni.yaml"
    oni_db_yaml = YamlReader(yaml_file=oni_db_yaml_file)
    db_path = oni_db_yaml.get_value("database.settings.file")
    # columns_to_check = ["ipv4", "physical_address", "hostname"]  # Specify the columns to check for duplicates
    columns_to_check = ["ipv4"]  # Specify the columns to check for duplicates
    InventoryCleaner(db_path=db_path)
