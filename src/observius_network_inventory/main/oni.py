from src.modules.common.LoggerSetup import LoggerSetup
from src.modules.yaml.YamlReader import YamlReader
from src.modules.sqlite.main import SQLiteManager
from src.modules.common.linux import create_dir, path_minus_file
from src.observius_network_inventory.configurators.mac.MacConfigurator import (
    MacConfigurator,
)
from src.observius_network_inventory.inventory.InventoryCleaner import InventoryCleaner
from src.observius_network_inventory.inventory.InventoryManager import InventoryManager
from src.observius_network_inventory.collector_manager.CollectorManager import (
    CollectorManager,
)


def main():
    """
    Observius Network Inventory (ONI) Main Process
    """
    # Configuration File Initialization
    oni_yaml_file = "resources/etc/oni/oni.yaml"
    oni_db_yaml_file = "resources/etc/databases/oni.yaml"
    oni_yaml = YamlReader(yaml_file=oni_yaml_file)
    oni_db_yaml = YamlReader(yaml_file=oni_db_yaml_file)

    # Variable Initialization
    program_name = oni_yaml.get_value("oni.settings.program_name")
    logging_level = oni_yaml.get_value("oni.settings.log_level")
    logging_path = oni_yaml.get_value("oni.settings.log_file_path")
    create_dir(path_minus_file(logging_path))

    # Logger Initialization
    logger = LoggerSetup(
        name=program_name, log_file=logging_path, level=logging_level
    ).get_logger()
    logger.info("Starting Observius Network Inventory (ONI)")
    logger.info(f'Configuration File: "{oni_yaml_file}" loaded successfully.')
    logger.info(f'Configuration File: "{oni_db_yaml_file}" loaded successfully.')

    # Database Initialization
    logger.info("Initializing ONI Database")
    oni_db = SQLiteManager(
        database_path=oni_db_yaml.get_value("database.settings.file")
    )
    create_dir(path_minus_file(oni_db_yaml.get_value("database.settings.file")))
    oni_db.create_database()
    oni_db.create_tables_from_yaml(yaml_path="resources/etc/databases/oni.yaml")
    logger.info("ONI Database Initialized")

    # Kick off collectors
    logger.info("Starting Collector Collectors")
    CollectorManager(db=oni_db, logger=logger).run_collectors()

    # Build Interface Inventory
    # InventoryManager(
    #     db=oni_db, logger=logger, config_path=oni_db_yaml_file
    # ).build_inventory

    # Build Master Inventory
    InventoryManager(
        db=oni_db, logger=logger, config_path=oni_db_yaml_file
    ).build_inventory()

    # Clean Master Inventory
    InventoryCleaner(db_path=oni_db_yaml.get_value("database.settings.file"))

    # Enrich MAC Addresses
    MacConfigurator(oni_db=oni_db)


if __name__ == "__main__":
    main()
