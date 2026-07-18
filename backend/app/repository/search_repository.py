"""
Repository layer for search document database operations.
Encapsulates MongoDB queries and document persistence.
"""

from typing import Optional, List
from pymongo.collection import Collection

from app.database.collections import get_search_collection
from app.models.search import SearchDocument
from app.utils.exceptions import DatabaseException


class SearchRepository:
    """
    Repository for search document CRUD operations.
    
    Provides abstraction layer between domain models and MongoDB persistence.
    
    Attributes:
        collection: MongoDB collection for search documents.
    """
    
    def __init__(self):
        """Initializes database collection reference."""
        self.collection: Collection = get_search_collection()

    def get_latest_search(self, keyword: str) -> Optional[SearchDocument]:
        """
        Retrieves the latest search document for a given keyword.
        
        Args:
            keyword: Search keyword to query.
            
        Returns:
            SearchDocument if found, None otherwise.
            
        Raises:
            DatabaseException: If query operation fails.
        """
        try:
            raw_dict = self.collection.find_one(
                {"keyword": keyword.strip().lower()},
                sort=[("version", -1)]
            )
            if not raw_dict:
                return None
            
            raw_dict.pop("_id", None)
            
            return SearchDocument(**raw_dict)
        except Exception as e:
            raise DatabaseException(f"Database query operation failed: {str(e)}")

    def create_search(self, search_document: SearchDocument) -> str:
        """
        Persists a new search document to the database.
        
        Args:
            search_document: SearchDocument to persist.
            
        Returns:
            String representation of the inserted document ID.
            
        Raises:
            DatabaseException: If insertion operation fails.
        """
        try:
            result = self.collection.insert_one(search_document.model_dump())
            return str(result.inserted_id)
        except Exception as e:
            raise DatabaseException(f"Database persist mutation failed: {str(e)}")

    def get_search_history(self, keyword: str) -> List[SearchDocument]:
        """
        Retrieves all historical versions of a search document.
        
        Args:
            keyword: Search keyword to query history for.
            
        Returns:
            List of SearchDocument instances sorted newest to oldest.
            
        Raises:
            DatabaseException: If query operation fails.
        """
        try:
            cursor = self.collection.find(
                {"keyword": keyword.strip().lower()}
            ).sort("version", -1)
            
            history_list = []
            for raw_dict in cursor:
                raw_dict.pop("_id", None)
                history_list.append(SearchDocument(**raw_dict))
                
            return history_list
        except Exception as e:
            raise DatabaseException(f"Failed to execute history query: {str(e)}")
