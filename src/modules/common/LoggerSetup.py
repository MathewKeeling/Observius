import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


class LoggerSetup:
    def __init__(self, name: str, log_file: Optional[str] = None, level: str = "INFO"):
        """
        Initialize logger with name and optional file output

        Args:
            name (str): Logger name
            log_file (Optional[str]): Path to log file (optional)
            level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Create formatters
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Add file handler if log_file is specified
        if log_file:
            try:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = RotatingFileHandler(
                    log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
                )
                file_handler.setFormatter(formatter)
                file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
                self.logger.addHandler(file_handler)
                print(f"File handler added: {file_handler}")
            except OSError as e:
                print(f"Error creating log file {log_file}: {e}")
                raise

        # Debug: Print all handlers
        for handler in self.logger.handlers:
            print(f"Handler: {handler}, Level: {handler.level}")

    def get_logger(self):
        """Return the configured logger"""
        return self.logger
