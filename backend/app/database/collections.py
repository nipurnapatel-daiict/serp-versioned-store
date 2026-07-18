"""
MongoDB collection access utilities.
Provides convenient access to database collections.
"""

from pymongo.collection import Collection

from app.config.settings import settings
from app.database.connection import MongoConnection


def get_search_collection() -> Collection:
    """
    Returns the search collection from the connected database.
    
    Returns:
        Collection: MongoDB collection for search documents.
    """
    database = MongoConnection.get_database()
    return database[settings.SEARCH_COLLECTION]
