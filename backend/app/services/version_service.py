"""
Version management service for search documents.
Calculates version numbers for new search documents.
"""

from app.utils.logger import logger


class VersionService:
    """Service for managing search document version numbers."""

    @staticmethod
    def get_next_version(latest_document: dict | None) -> int:
        """
        Calculates the incremental version sequence number.
        
        Args:
            latest_document: Latest search document or None for new keywords.
            
        Returns:
            Next version number (1 for new keywords, incremented for existing).
        """
        if latest_document is None:
            logger.info("No prior history found for keyword. Initializing at Version 1.")
            return 1

        current_version = latest_document.get("version", 1)
        next_version = current_version + 1
        
        logger.info(f"Prior record found at Version {current_version}. Incremented target pointer to Version {next_version}.")
        return next_version
