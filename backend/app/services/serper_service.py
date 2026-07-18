"""
Serper API integration service.
Fetches Google search results from Serper.dev API.
"""

import time
import requests
from typing import List, Dict, Any

from app.config.settings import settings
from app.models.search import SearchResult 
from app.utils.logger import logger
from app.utils.exceptions import SearchProviderException


class SerperService:
    """Service for fetching search results from Serper API."""

    def search(self, keyword: str) -> List[SearchResult]:
        """
        Fetches Google search results from Serper API.
        
        Implements retry logic for network resilience and maps responses
        to domain models.
        
        Args:
            keyword: Search term to query.
            
        Returns:
            List of SearchResult objects from the API response.
            
        Raises:
            SearchProviderException: If API request fails after retries.
        """
        headers = {
            "X-API-KEY": settings.SERPER_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "q": keyword,
            "num": 10
        }

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Calling Serper API for keyword='{keyword}' (Attempt {attempt}/{max_attempts})...")
                
                response = requests.post(
                    settings.SERPER_URL,
                    headers=headers,
                    json=payload,
                    timeout=settings.REQUEST_TIMEOUT,
                )

                if response.status_code in (401, 403):
                    raise SearchProviderException("Serper API access denied. Invalid or inactive credentials.")
                if response.status_code == 429:
                    raise SearchProviderException("Serper API request blocked: Quota limit exceeded.")
                
                response.raise_for_status()
                raw_data = response.json()
                
                organic_results = raw_data.get("organic", [])
                
                if not organic_results:
                    logger.warning(f"Serper API returned an empty result array for keyword '{keyword}'.")
                    return []

                parsed_results = []
                for index, item in enumerate(organic_results):
                    parsed_results.append(
                        SearchResult(
                            rank=item.get("position", len(parsed_results) + 1),
                            title=item.get("title", "Untitled Entry"),
                            url=item.get("link", ""),
                            snippet=item.get("snippet")  
                        )
                    )
                
                return parsed_results

            except requests.exceptions.Timeout as timeout_err:
                logger.warning(f"Attempt {attempt} failed: Serper connection timed out. Error: {timeout_err}")
                if attempt == max_attempts:
                    raise SearchProviderException("Serper API requests timed out after multiple attempts.")
                time.sleep(1)  
                
            except requests.exceptions.ConnectionError as conn_err:
                logger.warning(f"Attempt {attempt} failed: Network connection failure. Error: {conn_err}")
                if attempt == max_attempts:
                    raise SearchProviderException("Unable to establish connection to upstream Serper network nodes.")
                time.sleep(1)
                
            except requests.exceptions.HTTPError as http_err:
                logger.error(f"Serper API responded with a critical failure status code: {http_err}")
                raise SearchProviderException(f"Upstream search gateway returned an HTTP error: {http_err}")
                
            except requests.exceptions.RequestException as general_err:
                logger.error(f"An unhandled request execution anomaly occurred: {general_err}")
                raise SearchProviderException(f"Search provider transaction failure: {general_err}")
