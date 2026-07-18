"""
Search orchestration workflow coordinator.
Manages the complete search pipeline from cache check to persistence.
"""

import time
from datetime import datetime, timezone
from typing import Optional, Any, Dict

from app.models.enums import SearchStatus
from app.models.search import SearchDocument, SearchResult
from app.repository.search_repository import SearchRepository
from app.services.cache_service import CacheService
from app.services.version_service import VersionService
from app.services.serper_service import SerperService
from app.services.summary_service import SummaryService
from app.utils.logger import logger


class SearchOrchestrator:
    """
    Orchestrates the complete search workflow pipeline.
    
    Coordinates cache validation, external API calls, AI synthesis,
    and database persistence with performance tracking.
    
    Attributes:
        repository: SearchRepository for database operations.
        cache_service: CacheService for cache validation.
        version_service: VersionService for version management.
        serper_service: SerperService for external search API.
        ollama_service: SummaryService for AI synthesis.
    """
    
    def __init__(
        self,
        repository: SearchRepository,
        cache_service: CacheService,
        version_service: VersionService,
        serper_service: SerperService,
        ollama_service: SummaryService,
    ):
        """Initializes the orchestrator with required service dependencies."""
        self.repository = repository
        self.cache_service = cache_service
        self.version_service = version_service
        self.serper_service = serper_service
        self.ollama_service = ollama_service

    async def search(self, keyword: str) -> Dict[str, Any]:
        """
        Executes the complete search workflow with performance tracking.
        
        Pipeline steps:
        1. Check cache for existing valid results
        2. If cache miss, call external API
        3. Generate AI synthesis if results exist
        4. Persist document with performance metrics
        
        Args:
            keyword: Search term to process.
            
        Returns:
            Dictionary with 'document' (SearchDocument) and 'cached' (bool).
        """
        start_perf = time.perf_counter()

        logger.info(f"Searching keyword='{keyword}'")

        latest: Optional[SearchDocument] = self.repository.get_latest_search(keyword)
        
        historical_logs = []
        if latest and hasattr(latest, "performance_history") and latest.performance_history:
            historical_logs = list(latest.performance_history)
        elif latest and isinstance(latest, dict) and "performance_history" in latest:
            historical_logs = list(latest["performance_history"])

        if latest and self.cache_service.is_cache_valid(latest.model_dump()):
            logger.info(f"Cache hit for keyword='{keyword}'. Returning cached version={latest.version}")
            
            turnaround_time = time.perf_counter() - start_perf
            now_iso_cache = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            
            cache_log_entry = {
                "timestamp": now_iso_cache,
                "turnaround_time_seconds": round(turnaround_time, 4),
                "execution_type": "60s Cache Hit",
                "version": latest.version
            }
            
            historical_logs.append(cache_log_entry)
            latest.performance_history = historical_logs
            
            self.repository.create_search(latest)
            return {"document": latest, "cached": True}

        logger.info(f"Cache miss for keyword='{keyword}'. Calling Serper API")
        
        results: list[SearchResult] = self.serper_service.search(keyword)
        logger.info(f"Received {len(results)} results from Serper API")

        latest_dict_fallback = latest.model_dump() if latest else None
        version = self.version_service.get_next_version(latest_dict_fallback)
        status = SearchStatus.SUCCESS if results else SearchStatus.NO_RESULTS

        ai_synthesis = None
        if results:
            ai_synthesis = await self.ollama_service.generate_summary(keyword, results)

        now_iso_live = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        turnaround_time = time.perf_counter() - start_perf

        live_log_entry = {
            "timestamp": now_iso_live,
            "turnaround_time_seconds": round(turnaround_time, 2),
            "execution_type": "Live Pipeline Run",
            "version": version
        }
        historical_logs.append(live_log_entry)

        document = SearchDocument(
            keyword=keyword,
            version=version,
            status=status,
            ai_synthesis=ai_synthesis,
            results=results,
            searched_at=now_iso_live,
            performance_history=historical_logs
        )

        self.repository.create_search(document)
        logger.info(f"Stored version={version} for keyword='{keyword}' successfully")
        
        return {"document": document, "cached": False}
