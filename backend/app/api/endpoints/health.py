"""
Health check endpoint for system monitoring.
Verifies database connectivity and application status.
"""

from fastapi import APIRouter, status
from app.database.connection import MongoConnection
from app.utils.response import success_response, error_response

router = APIRouter()


@router.get("", summary="System Health Verification Checklist")
def health_check():
    """
    Verifies that the microservice tier can actively communicate 
    with underlying storage systems before returning status states.
    
    Returns:
        dict: Health status with database connection state.
        
    Raises:
        JSONResponse: 503 error if database is unreachable.
    """
    try:
        db = MongoConnection.get_database()
        db.client.admin.command("ping")

        return success_response(
            message="Application is fully functional.",
            data={
                "status": "healthy",
                "database": "connected"
            }
        )
    except Exception as err:
        return error_response(
            message=f"System degradation detected. Database unreachable: {str(err)}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
