"""
Centralized logging configuration with file rotation.
Provides singleton logger instance with console and file handlers.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from app.config.settings import get_settings


class LoggerManager:
    """
    Singleton logger manager with rotating file handler.
    
    Provides centralized logging configuration with both console
    and file output, supporting log rotation for size management.
    
    Attributes:
        settings: Application settings instance.
        LOGGER_NAME: Name for the logger instance.
        LOG_DIRECTORY: Directory path for log files.
        LOG_FILE: Full path to the log file.
    """
    
    settings = get_settings()
    
    LOGGER_NAME = settings.APP_NAME.lower().replace(" ", "-")
    
    LOG_DIRECTORY = os.getenv("LOG_DIR_PATH", "logs")
    LOG_FILE = f"{LOG_DIRECTORY}/app.log"

    @classmethod
    def get_logger(cls):
        """
        Creates and returns a configured logger instance.
        
        Sets up console and rotating file handlers with standardized
        formatting. Falls back to /tmp/logs if default directory
        creation fails.
        
        Returns:
            logging.Logger: Configured logger instance.
        """
        try:
            os.makedirs(cls.LOG_DIRECTORY, exist_ok=True)
        except OSError:
            cls.LOG_DIRECTORY = "/tmp/logs"
            cls.LOG_FILE = f"{cls.LOG_DIRECTORY}/app.log"
            os.makedirs(cls.LOG_DIRECTORY, exist_ok=True)

        logger = logging.getLogger(cls.LOGGER_NAME)
        
        if logger.handlers:
            return logger

        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(filename)s:%(lineno)d | "
            "%(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        file_handler = RotatingFileHandler(
            cls.LOG_FILE,
            maxBytes=1024 * 1024, 
            backupCount=5
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        return logger
    
logger = LoggerManager.get_logger()
