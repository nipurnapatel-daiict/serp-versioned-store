"""
Enumeration types for search domain models.
Defines status and provider constants for search operations.
"""

from enum import Enum


class SearchStatus(str, Enum):
    """Search operation status enumeration."""
    SUCCESS = "SUCCESS"
    NO_RESULTS = "NO_RESULTS"


class SearchProvider(str, Enum):
    """Search provider service enumeration."""
    SERPER = "SERPER"
