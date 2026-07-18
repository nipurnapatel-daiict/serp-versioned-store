"""
Database index creation and management.
Ensures optimal query performance through proper indexing.
"""

from pymongo import ASCENDING, DESCENDING
from app.database.collections import get_search_collection
from app.utils.logger import logger


def create_indexes():
    """
    Ensures optimal database indexes exist on application bootstrap.
    
    Creates compound indexes for:
    - keyword + version: Optimizes cache checks and version increments.
    - keyword + searched_at: Optimizes chronological audit trail queries.
    """
    try:
        collection = get_search_collection()
        logger.info("Initializing database index validation sequences...")

        collection.create_index(
            [
                ("keyword", ASCENDING),
                ("version", DESCENDING)
            ],
            name="idx_keyword_version"
        )

        collection.create_index(
            [
                ("keyword", ASCENDING),
                ("searched_at", DESCENDING)
            ],
            name="idx_keyword_searched_at"
        )

        logger.info("MongoDB structural database indexes validated and active.")
        
    except Exception as e:
        logger.error(f"Critical error creating MongoDB index topologies: {str(e)}")
