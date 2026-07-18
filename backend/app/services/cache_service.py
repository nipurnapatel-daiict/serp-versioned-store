"""
Cache validation service for search documents.
Determines if cached results are still valid based on expiry time.
"""

from datetime import datetime, timezone
from app.config.settings import settings
from app.utils.logger import logger


class CacheService:
    """Service for validating cache freshness of search documents."""

    @staticmethod
    def is_cache_valid(document: dict) -> bool:
        """
        Evaluates whether a keyword document was fetched within the cache boundary.
        
        Args:
            document: Search document dictionary containing 'searched_at' field.
            
        Returns:
            True if document is within cache expiry window, False otherwise.
        """
        if document is None:
            return False

        try:
            searched_at_raw = document.get("searched_at")
            if not searched_at_raw:
                return False

            sanitized_time_str = searched_at_raw.replace("Z", "+00:00")

            past_time = datetime.fromisoformat(sanitized_time_str)
            
            current_time = datetime.now(timezone.utc)

            elapsed_seconds = (current_time - past_time).total_seconds()
            
            is_valid = elapsed_seconds < settings.CACHE_EXPIRY_SECONDS
            
            if is_valid:
                logger.info(
                    f"Cache hit verified for keyword '{document.get('keyword')}'. "
                    f"Record age: {elapsed_seconds:.2f}s (Threshold: {settings.CACHE_EXPIRY_SECONDS}s)."
                )
            else:
                logger.info(f"Cache expired for keyword '{document.get('keyword')}'. Age: {elapsed_seconds:.2f}s.")
                
            return is_valid

        except (ValueError, TypeError) as parse_error:
            logger.error(f"Cache service temporal boundary math validation failure: {str(parse_error)}")
            return False
