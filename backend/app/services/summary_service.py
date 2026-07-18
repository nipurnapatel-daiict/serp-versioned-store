"""
Ollama AI synthesis service.
Generates text summaries using local LLM (Mistral 7B).
"""

import httpx
from typing import List
from app.config.settings import settings
from app.models.search import SearchResult
from app.utils.logger import logger


class SummaryService:
    """Service for generating AI-powered summaries using Ollama."""

    def __init__(self):
        """Initializes connection parameters for the local Ollama node."""
        self.ollama_url = settings.OLLAMA_URL

    async def generate_summary(
        self, keyword: str, results: List[SearchResult]
    ) -> str | None:
        """
        Assembles context tokens from top search snippets and requests
        a single-paragraph synthesis from a local Mistral 7B instance.
        
        Args:
            keyword: Search keyword for context.
            results: List of SearchResult objects to synthesize.
            
        Returns:
            Generated summary string or None if synthesis fails.
        """
        if not results:
            logger.warning(
                f"Skipping summary for keyword='{keyword}': No search results available."
            )
            return None

        context_items = []
        for item in results[:5]:
            snippet_text = item.snippet or "No description preview available."
            context_items.append(
                f"- Title: {item.title}\n  Snippet: {snippet_text}"
            )

        context_blob = "\n".join(context_items)

        prompt = (
            f"You are a professional research analyst assistant.\n"
            f"Review these Google search results for the keyword or phrase: '{keyword}'.\n"
            f"Generate a single, dense, comprehensive paragraph explaining what these results collectively show about the user's intent or current market trends.\n"
            f"CRITICAL COMPLIANCE: Do not use introductory phrases, markdown bullet points, greeting headers, or conversational filler. "
            f"Output exactly one paragraph of pure text text.\n\n"
            f"Search Results:\n{context_blob}"
        )

        payload = {
            "model": "mistral:latest",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 4096,
                "top_p": 0.9,
                "num_predict": 256,
                "num_thread": 4
            }
        }

        generation_timeout = max(
            float(getattr(settings, "REQUEST_TIMEOUT", 10.0)), 60.0
        )

        try:
            base_url = str(self.ollama_url).rstrip("/")
            if not base_url.endswith("/api/generate"):
                target_url = f"{base_url}/api/generate"
            else:
                target_url = base_url

            logger.info(
                f"Calling Ollama API asynchronously at {target_url} for keyword='{keyword}'..."
            )

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    target_url, json=payload, timeout=generation_timeout
                )

            if response.status_code == 200:
                summary_text = response.json().get("response", "").strip()
                logger.info(
                    f"Generated summary successfully for keyword='{keyword}'"
                )
                return summary_text

            logger.error(
                f"Ollama rejected request with status code {response.status_code}: {response.text}"
            )

        except httpx.TimeoutException:
            logger.error(
                f"Ollama generation timed out after {generation_timeout} seconds on AK-CPU."
            )
        except httpx.RequestError as exc:
            logger.error(
                f"Network connection error calling Ollama at {exc.request.url!r}: {str(exc)}"
            )
        except Exception as general_exc:
            logger.error(
                f"Critical unexpected exception inside SummaryService: {str(general_exc)}",
                exc_info=True,
                stack_info=True,
            )

        return None
