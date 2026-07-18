"""
MongoDB connection manager with retry logic and health checks.
Provides thread-safe singleton database connection handling.
"""

import time
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure

from app.config.settings import settings
from app.utils.logger import logger


class MongoConnection:
    """
    Thread-safe, Docker-resilient Singleton MongoDB Connection Manager.
    
    Provides centralized database connection management with automatic retry
    logic for container startup timing issues.
    
    Attributes:
        _client: Singleton MongoClient instance.
        _database: Singleton Database instance.
    """

    _client: MongoClient = None
    _database: Database = None

    @classmethod
    def get_database(cls) -> Database:
        """
        Establishes and returns the MongoDB database connection.
        
        Implements exponential backoff retry logic for Docker container
        startup timing resilience.
        
        Returns:
            Database: Connected MongoDB database instance.
            
        Raises:
            ConnectionFailure: If connection fails after max retries.
        """
        if cls._database is None:
            logger.info("Initializing database connection manager...")
            
            max_retries = 5
            backoff_factor = 2
            
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"Connecting to MongoDB (Attempt {attempt}/{max_retries})...")
                    cls._client = MongoClient(
                        settings.MONGO_URI,
                        serverSelectionTimeoutMS=5000 
                    )
                    
                    cls._client.admin.command("ping")
                    
                    cls._database = cls._client[settings.DATABASE_NAME]
                    logger.info("MongoDB connection verified successfully.")
                    break
                    
                except ConnectionFailure as err:
                    if attempt == max_retries:
                        logger.critical("Could not connect to MongoDB. Max retries exceeded.")
                        raise err
                    
                    sleep_time = backoff_factor ** attempt
                    logger.warning(f"MongoDB not ready yet. Retrying in {sleep_time}s... Error: {err}")
                    time.sleep(sleep_time)

        return cls._database

    @classmethod
    def close_connection(cls):
        """
        Cleanly closes the MongoDB connection pool.
        
        Should be called during application shutdown to release resources.
        """
        if cls._client is not None:
            logger.info("Closing MongoDB connection pool gracefully...")
            cls._client.close()
            cls._client = None
            cls._database = None
            logger.info("MongoDB connection pool terminated.")
