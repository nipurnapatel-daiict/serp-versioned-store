"""
FastAPI application entry point for the Search Analytics microservice.
Handles application lifecycle, exception handling, and API router registration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config.settings import settings
from app.database.connection import MongoConnection
from app.database.indexes import create_indexes
from app.utils.exceptions import ApplicationException
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages centralized setup and teardown tasks for the application state.
    
    Args:
        app: FastAPI application instance.
        
    Yields:
        Control to the application during its lifetime.
        
    Raises:
        Exception: If database initialization fails during startup.
    """
    logger.info("Initializing search microservice cluster configurations...")
    try:
        MongoConnection.get_database()
        create_indexes()
    except Exception as initialization_error:
        logger.critical(f"Container bootstrap failed during lifespan init: {initialization_error}")
        raise initialization_error

    yield

    logger.info("Server termination hook intercepted. Initiating cleanup operations...")
    MongoConnection.close_connection()
    logger.info("Application context terminated safely.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    redirect_slashes=True
)


@app.exception_handler(ApplicationException)
async def application_exception_handler(
    request: Request,
    exc: ApplicationException,
):
    """
    Globally intercepts domain level business errors to output formatted 
    JSON tracking responses matching custom status configurations.
    
    Args:
        request: The incoming HTTP request.
        exc: The raised ApplicationException instance.
        
    Returns:
        JSONResponse with error details and appropriate status code.
    """
    logger.warning(f"Business Domain Exception Intercepted: {exc.message} [Code: {exc.status_code}]")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Safety wrapper intercepts unhandled low-level language or platform crashes 
    to log complete diagnostics while keeping public payloads opaque.
    
    Args:
        request: The incoming HTTP request.
        exc: The unhandled exception instance.
        
    Returns:
        JSONResponse with generic error message and 500 status code.
    """
    logger.exception(f"Unhandled critical system error captured: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unhandled internal system failure occurred. Please check cluster server logs.",
        },
    )

app.include_router(api_router, prefix="/api/v1")


@app.get("/", summary="Root API Operational Vital Check")
def root():
    """
    Provides a simple base verification route for reverse proxy mappings.
    
    Returns:
        dict: Application status with name and version.
    """
    return {
        "success": True,
        "message": f"{settings.APP_NAME} operational nodes active.",
        "version": settings.APP_VERSION,
    }
