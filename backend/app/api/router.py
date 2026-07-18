"""
API router configuration module.
Registers all endpoint routers under a unified API structure.
"""

from fastapi import APIRouter

from app.api.endpoints.health import router as health_router
from app.api.endpoints.search import router as search_router

api_router = APIRouter()

api_router.include_router(
    health_router,
    prefix="/health",
    tags=["Health Monitoring Interface"]
)

api_router.include_router(
    search_router,
    prefix="/search",
    tags=["Search Core Engine Node Layout"]
)
