import pandas as pd
import sqlite3
import os
import logging
import yaml
from src.modules.yaml.YamlReader import YamlReader


class SQLiteManager:
    def __init__(self, database_path: str):
        self.database_path = database_path

    def build_batch_insert_command(
        self, table_name: str, data_list: list, conflict_resolution: str = "ignore"
    ) -> str:
        """
        Build an SQL query to insert a list of dictionaries containing data into a SQLite table.

        Args:
            table_name (str): The name of the table.
            data_list (list): A list of dictionaries representing the data to be inserted.
                Each dictionary should have the same keys, which correspond to the column names.
            conflict_resolution (str): Conflict resolution strategy, either "ignore" or "replace".

        Returns:
            str: The SQL query and a tuple of values to be inserted.

        Raises:
            ValueError: If the data_list is empty or if the dictionaries have different keys.
            ValueError: If conflict_resolution is not "ignore" or "replace".
        """
        if not data_list or not all(len(d) == len(data_list[0]) for d in data_list):
            raise ValueError(
                "All dictionaries must have the same number of keys and the list should not be empty."
            )

        if conflict_resolution not in ["ignore", "replace"]:
            raise ValueError(
                "conflict_resolution must be either 'ignore' or 'replace'."
            )

        columns = ", ".join(data_list[0].keys())
        placeholders = ", ".join("?" for _ in data_list[0].values())
        values = [tuple(d.values()) for d in data_list]

        if conflict_resolution == "ignore":
            sql_command = f"INSERT OR IGNORE INTO {table_name} ({columns}) VALUES ({placeholders})"
        else:
            sql_command = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"

        return sql_command, values

    def build_insert_command(self, table_name: str, data: dict) -> str:
        """
        Build an SQL query to insert a dictionary of data into a SQLite table.

        Args:
            table_name (str): The name of the table.
            data (dict): A dictionary representing the data to be inserted.
                The keys should correspond to the column names and the values
                should correspond to the values to be inserted.

        Returns:
            str: The SQL query.

        Raises:
            None
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data.values())
        sql_command = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        return sql_command, tuple(data.values())

    def create_database(self) -> None:
        """
        Creates a new SQLite database at the specified path if it doesn't exist.

        Args:
            None

        Returns:
            None
        """

        if os.path.exists(self.database_path):
            logging.info(f"Database already exists at {self.database_path}")
            return

        try:
            conn = sqlite3.connect(self.database_path)
            conn.close()
            logging.info(f"Created new database at {self.database_path}")
        except sqlite3.Error as e:
            logging.error(
                f"Failed to create database at {self.database_path}: {str(e)}"
            )
            raise

    def create_table(
        self, table_name: str, columns: list, unique_constraints: list = None
    ):
        """
        Create a table in a SQLite database with the specified columns.

        Args:
            table_name (str): The name of the table.
            columns (list): A list of dictionaries representing the columns of the table.
                Each dictionary should have the keys 'column' and 'data_type',
                specifying the name and data type of the column, respectively.
            unique_constraints (list): A list of dictionaries representing unique constraints.
                Each dictionary should have the key 'columns', which is a list of column names.

        Returns:
            None

        Raises:
            None
        """
        # Connect to the database (or create it if it doesn't exist)
        conn = sqlite3.connect(self.database_path)
        # Create a cursor object to execute SQL statements
        cursor = conn.cursor()

        # Create the table if it doesn't already exist
        column_definitions = []
        for column in columns:
            column_name = column["column"]
            data_type = column["data_type"]
            column_definition = f"{column_name} {data_type}"
            column_definitions.append(column_definition)

        # Extract unique constraint columns
        unique_columns = []
        for constraint in unique_constraints:
            unique_columns.extend(constraint["columns"])

        unique_clause = (
            f", UNIQUE ({', '.join(unique_columns)})" if unique_columns else ""
        )

        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY,
                {', '.join(column_definitions)}
                {unique_clause}
            )
        """
        cursor.execute(create_table_query)

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    def create_tables_from_yaml(self, yaml_path: str):
        """
        Create tables in the SQLite database based on the YAML schema definitions.

        Args:
            yaml_path (str): Path to the YAML file containing the schema definitions
        """
        yaml_reader = YamlReader(yaml_path)
        tables = yaml_reader.get_value("database.tables")

        for table in tables:
            table_name = table["name"]
            schema = table["schema"]

            schema_columns = schema["columns"]
            unique_constraints = schema.get("unique_constraints", [])

            column_definitions = [
                {"column": col["name"], "data_type": col["type"]}
                for col in schema_columns
            ]

            self.create_table(table_name, column_definitions, unique_constraints)
            self.update_table_schema(table_name, column_definitions)

    def execute_batch_insert(self, command: str, values: list):
        """
        Execute a batch insert using a pre-built SQL command and a list of tuples containing the values.

        Args:
            command (str): The pre-built SQL insert command.
            values (list): A list of tuples representing the data to be inserted.

        Returns:
            None

        Raises:
            None
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        try:
            cursor.executemany(command, values)
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Failed to execute batch insert: {str(e)}")
        finally:
            conn.close()

    def execute_sqlite_command(self, command: str, values: tuple, params=None) -> list:
        """
        Legacy method to execute a given SQL command with optional parameters and return the results.
        Should be replaced with execute_sqlite_query. (Dataframe)
        """
        # Connect to the database (or create it if it doesn't exist)
        conn = sqlite3.connect(self.database_path)
        # Create a cursor object to execute SQL statements
        cursor = conn.cursor()
        # Execute the command with optional parameters
        if params:
            cursor.execute(command, values, params)
        else:
            cursor.execute(command, values)
        # Fetch the results if any
        results = cursor.fetchall()
        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        # Return the results
        return results

    def execute_sqlite_query(self, query: str, params: tuple = ()):
        """
        Execute a given SQL query with optional parameters and return the results as a DataFrame.

        Args:
            query (str): The SQL query to execute.
            params (tuple): Optional parameters to include in the query.

        Returns:
            DataFrame: A pandas DataFrame containing the rows returned by the query.
        """
        conn = sqlite3.connect(self.database_path)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df

    def update_table_schema(self, table_name: str, columns: list):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = {col[1]: col[2] for col in cursor.fetchall()}

        for column in columns:
            column_name = column["column"]
            data_type = column["data_type"]
            if column_name not in existing_columns:
                cursor.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type}"
                )
            elif existing_columns[column_name] != data_type:
                logging.warning(
                    f"Column {column_name} type mismatch: {existing_columns[column_name]} vs {data_type}"
                )

        conn.commit()
        conn.close()


def main():
    pass


if __name__ == "__main__":
    # Call the main function
    print()
