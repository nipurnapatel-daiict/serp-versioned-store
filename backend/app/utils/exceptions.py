"""
Custom exception classes for the application.
Defines domain-specific exceptions with HTTP status code mapping.
"""

from fastapi import status


class ApplicationException(Exception):
    """
    Base exception for all application-level errors.
    
    Attributes:
        message: Human-readable error message.
        status_code: HTTP status code for the error response.
    """
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DatabaseException(ApplicationException):
    """Exception for database timeouts, replication locks, or connection failures."""
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class SearchProviderException(ApplicationException):
    """Exception for captcha blocks, quota exhaustion, or invalid API key states."""
    def __init__(self, message: str, status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class LLMProviderException(ApplicationException):
    """Exception for local Ollama container timeout or connection drops."""
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CacheException(ApplicationException):
    """Exception for temporal calculation validation failures."""
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidationException(ApplicationException):
    """Exception for empty keywords, spaces, or malformed text parameters."""
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)
