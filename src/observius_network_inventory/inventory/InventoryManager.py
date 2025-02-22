import sqlite3
from src.modules.sqlite.main import SQLiteManager
from src.modules.common.LoggerSetup import LoggerSetup
from src.modules.yaml.YamlReader import YamlReader


class InventoryManager:
    """
    A class to manage and build the inventory from multiple database tables.
    """

    def __init__(self, db: SQLiteManager, logger: LoggerSetup, config_path: str):
        """
        Initialize the InventoryManager with the database manager, logger, and configuration path.

        :param db: An instance of SQLiteManager to manage database operations.
        :param logger: An instance of LoggerSetup for logging.
        :param config_path: Path to the YAML configuration file.
        """
        self.db = db
        self.logger = logger
        self.config = YamlReader(config_path).get_value("database")

    def gather_data(self):
        """
        Gather data from all tables specified in the YAML configuration.

        :return: A list of all data from the specified tables.
        """
        tables = self.get_table_names_from_yaml()
        all_data = []
        for table in tables:
            data = self.fetch_table_data(table)
            all_data.extend(data)
        return all_data

    def get_table_names_from_yaml(self):
        """
        Get the names of the tables from the YAML configuration.

        :return: A list of table names.
        """
        tables = self.config["tables"]
        return [table["name"] for table in tables]

    def fetch_table_data(self, table_name):
        """
        Fetch data from a specific table and add a 'source' column with the table name.

        :param table_name: The name of the table to fetch data from.
        :return: A list of dictionaries containing the table data.
        """
        query = f"SELECT *, '{table_name}' as source FROM {table_name}"
        conn = sqlite3.connect(self.db.database_path)
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        conn.close()

        # Convert rows to list of dictionaries
        data = [dict(zip(columns, row)) for row in rows]
        return data

    def build_inventory(self):
        """
        Build the master inventory by gathering data from all specified tables and saving it to the master_inventory table.
        """
        all_data = self.gather_data()
        self.save_to_master_inventory(all_data)

    def save_to_master_inventory(self, all_data):
        """
        Save the gathered data to the master_inventory table.

        :param all_data: A list of dictionaries containing all the gathered data.
        """
        conn = sqlite3.connect(self.db.database_path)
        cursor = conn.cursor()

        # Get the columns of the master_inventory table, excluding the 'id' column
        cursor.execute("PRAGMA table_info(master_inventory)")
        columns_info = cursor.fetchall()
        columns = [info[1] for info in columns_info if info[1] != "id"]

        cursor.execute("DELETE FROM master_inventory")

        # Insert data into master_inventory using named columns
        for device in all_data:
            placeholders = ", ".join([f":{col}" for col in columns])
            query = f"INSERT INTO master_inventory ({', '.join(columns)}) VALUES ({placeholders})"
            cursor.execute(query, {col: device.get(col) for col in columns})

        conn.commit()
        conn.close()
