"""
Search endpoint for keyword processing and result retrieval.
Handles POST requests for keyword search operations.
"""

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_search_orchestrator
from app.orchestration.search_orchestrator import SearchOrchestrator
from app.schemas.request import SearchRequest
from app.schemas.response import SearchResponse, SearchResultResponse

router = APIRouter()


@router.post(
    "",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest and process organic keyword layouts"
)
async def search_keyword(
    request: SearchRequest,
    orchestrator: SearchOrchestrator = Depends(get_search_orchestrator),
):
    """
    Exposes a unified POST entry point to validate incoming payload keywords,
    invoke search business pipelines, and output type-safe analytics models.
    
    Args:
        request: SearchRequest containing the keyword to search.
        orchestrator: Injected SearchOrchestrator for workflow execution.
        
    Returns:
        SearchResponse with search results, metadata, and performance history.
    """
    workflow_result = await orchestrator.search(request.keyword)
    
    document = workflow_result["document"]
    is_cached = workflow_result["cached"]

    formatted_results = [
        SearchResultResponse(rank=r.rank, title=r.title, url=r.url, snippet=r.snippet)
        for r in document.results
    ]

    return SearchResponse(
        keyword=document.keyword,
        version=document.version,
        cached=is_cached,
        searched_at=document.searched_at,  
        ai_synthesis=document.ai_synthesis, 
        results=formatted_results,
        performance_history=document.performance_history
    )
