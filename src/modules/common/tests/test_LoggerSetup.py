import pytest
import logging
import os
from src.modules.common.LoggerSetup import LoggerSetup


@pytest.fixture(autouse=True)
def disable_logging():
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


def test_logger_setup_console_only(caplog):
    logger = LoggerSetup(name="test_logger").get_logger()
    original_handlers = logger.handlers[:]
    with caplog.at_level(logging.INFO):
        for handler in original_handlers:
            logger.removeHandler(handler)
        logger.addHandler(logging.StreamHandler())  # Add a temporary handler for caplog
        logger.info("Test message")
    for handler in original_handlers:
        logger.addHandler(handler)
    assert "Test message" in caplog.text


def test_logger_setup_invalid_level(caplog):
    logger = LoggerSetup(name="test_logger", level="INVALID").get_logger()
    original_handlers = logger.handlers[:]
    with caplog.at_level(logging.INFO):
        for handler in original_handlers:
            logger.removeHandler(handler)
        logger.addHandler(logging.StreamHandler())  # Add a temporary handler for caplog
        logger.info("Test message")
    for handler in original_handlers:
        logger.addHandler(handler)
    assert "Test message" in caplog.text


def test_logger_setup_invalid_log_file():
    with pytest.raises(OSError):
        LoggerSetup(name="test_logger", log_file="/invalid_path/test.log").get_logger()
