import unittest
from src.modules.yaml.YamlReader import YamlReader
from unittest.mock import MagicMock
from src.observius_network_inventory.collector_manager.CollectorManager import (
    CollectorManager,
)


class TestCollectorManager(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.logger = MagicMock()
        self.collector_manager = CollectorManager(db=self.db, logger=self.logger)

    def test_load_config(self):
        self.collector_manager.yaml_reader.get_section = MagicMock(
            return_value={"dns_ad": {"enabled": True}}
        )
        config = self.collector_manager.load_config()
        self.assertIn("dns_ad", config)
        self.assertTrue(config["dns_ad"]["enabled"])

    def test_run_collectors(self):
        self.collector_manager.collectors = {"dns_ad": {"enabled": True}}
        self.collector_manager.run_collector = MagicMock()

        self.collector_manager.run_collectors()
        self.collector_manager.run_collector.assert_called_with("dns_ad")


if __name__ == "__main__":
    unittest.main()
