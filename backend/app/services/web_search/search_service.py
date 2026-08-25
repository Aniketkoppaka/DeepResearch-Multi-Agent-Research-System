"""
Web Search Engine coordinator.
Orchestrates Tavily primary and DuckDuckGo fallback searches.
"""

import logging
import os
from typing import List, Optional

from app.services.web_search.base import SearchProvider, WebSearchResult
from app.services.web_search.duckduckgo_provider import DuckDuckGoProvider
from app.services.web_search.tavily_provider import TavilyProvider

logger = logging.getLogger(__name__)


class WebSearchEngine:
    def __init__(
        self,
        tavily_api_key: Optional[str] = None,
        primary_provider: Optional[SearchProvider] = None,
        fallback_provider: Optional[SearchProvider] = None,
    ) -> None:
        key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        self.primary_provider = primary_provider or (
            TavilyProvider(api_key=key) if key else None
        )
        self.fallback_provider = fallback_provider or DuckDuckGoProvider()

    async def search(
        self,
        query: str,
        max_results: int = 5,
        allowed_domains: Optional[List[str]] = None,
    ) -> List[WebSearchResult]:
        if not query.strip():
            return []

        # 1. Try primary provider (Tavily if key present)
        if self.primary_provider:
            try:
                results = await self.primary_provider.search(
                    query=query,
                    max_results=max_results,
                    allowed_domains=allowed_domains,
                )
                if results:
                    return results
            except Exception as exc:
                logger.warning("Primary search provider failed: %s. Using fallback.", exc)

        # 2. Use fallback provider (DuckDuckGo)
        return await self.fallback_provider.search(
            query=query,
            max_results=max_results,
            allowed_domains=allowed_domains,
        )
