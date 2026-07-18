"""
Search result parsing service.
Transforms raw API responses into domain models.
"""

from app.models.search import SearchResult


class SearchService:
    """Service for parsing raw search API responses."""

    @staticmethod
    def parse_results(response: dict) -> list[SearchResult]:
        """
        Transforms raw Serper API JSON arrays into strongly-typed SearchResult objects.
        
        Args:
            response: Raw API response dictionary.
            
        Returns:
            List of SearchResult objects.
        """
        organic = response.get("organic", [])
        results = []

        for item in organic:
            result = SearchResult(
                rank=item.get("position", len(results) + 1),
                title=item.get("title", "Untitled Content Entry"),
                url=item.get("link", ""),
                snippet=item.get("snippet")  
            )
            results.append(result)

        return results
