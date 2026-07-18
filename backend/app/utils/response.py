"""
API response helper utilities.
Provides standardized response formatting functions.
"""

from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(
    message: str,
    data: Any = None
) -> dict:
    """
    Standard dictionary formatter for successful workflow execution.
    
    Args:
        message: Success message string.
        data: Optional payload data.
        
    Returns:
        Formatted success response dictionary.
    """
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(
    message: str,
    status_code: int,
) -> JSONResponse:
    """
    Returns a FastAPI JSONResponse for error states.
    
    Allows bypassing standard route mapping to send error
    metrics back to the UI immediately.
    
    Args:
        message: Error message string.
        status_code: HTTP status code for the response.
        
    Returns:
        JSONResponse with error details.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "status_code": status_code,
        }
    )
