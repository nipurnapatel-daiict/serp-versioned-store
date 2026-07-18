"""
FastAPI dependency injection configuration.
Provides service and repository instances to endpoint handlers.
"""

from fastapi import Depends
from app.orchestration.search_orchestrator import SearchOrchestrator
from app.repository.search_repository import SearchRepository
from app.services.cache_service import CacheService
from app.services.serper_service import SerperService
from app.services.version_service import VersionService
from app.services.summary_service import SummaryService


def get_repository() -> SearchRepository:
    """Returns a SearchRepository instance."""
    return SearchRepository()


def get_cache_service() -> CacheService:
    """Returns a CacheService instance."""
    return CacheService()


def get_version_service() -> VersionService:
    """Returns a VersionService instance."""
    return VersionService()


def get_serper_service() -> SerperService:
    """Returns a SerperService instance."""
    return SerperService()


def get_ollama_service() -> SummaryService:
    """Returns a SummaryService instance."""
    return SummaryService()


def get_search_orchestrator(
    repository: SearchRepository = Depends(get_repository),
    cache_service: CacheService = Depends(get_cache_service),
    version_service: VersionService = Depends(get_version_service),
    serper_service: SerperService = Depends(get_serper_service),
    ollama_service: SummaryService = Depends(get_ollama_service),
) -> SearchOrchestrator:
    """
    Constructs a SearchOrchestrator with all required dependencies.
    
    Args:
        repository: SearchRepository for database operations.
        cache_service: CacheService for cache validation.
        version_service: VersionService for version management.
        serper_service: SerperService for external API calls.
        ollama_service: SummaryService for AI synthesis.
        
    Returns:
        Configured SearchOrchestrator instance.
    """
    return SearchOrchestrator(
        repository=repository,
        cache_service=cache_service,
        version_service=version_service,
        serper_service=serper_service,
        ollama_service=ollama_service
    )
