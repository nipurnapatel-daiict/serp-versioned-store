"""
Backend API client module.
Handles HTTP communication with the FastAPI backend service.
"""

import requests
import os

BASE_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000/api/v1"
)


class APIClient:
    """Client for making HTTP requests to the backend API."""

    @staticmethod
    def search(keyword: str):
        """
        Sends a search request to the backend API.
        
        Args:
            keyword: Search term to query.
            
        Returns:
            dict: JSON response from the backend containing search results.
            
        Raises:
            requests.HTTPError: If the request fails.
        """
        response = requests.post(
            f"{BASE_URL}/search",
            json={"keyword": keyword.strip()},
            timeout=120
        )
        response.raise_for_status()
        return response.json()
