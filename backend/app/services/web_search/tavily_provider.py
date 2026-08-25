"""
Tavily Search Provider implementation for high-quality web research.
"""

import logging
from typing import List, Optional
from urllib.parse import urlparse

import httpx

from app.services.web_search.base import WebSearchResult

logger = logging.getLogger(__name__)


class TavilyProvider:
    def __init__(self, api_key: Optional[str] = None, timeout: float = 15.0) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.endpoint = "https://api.tavily.com/search"

    async def search(
        self,
        query: str,
        max_results: int = 5,
        allowed_domains: Optional[List[str]] = None,
    ) -> List[WebSearchResult]:
        if not self.api_key or not query.strip():
            return []

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": max_results,
            "include_domains": allowed_domains or [],
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(self.endpoint, json=payload)
                if res.status_code != 200:
                    logger.warning("Tavily API error: status %d", res.status_code)
                    return []

                data = res.json()
                results: List[WebSearchResult] = []
                for item in data.get("results", []):
                    url = item.get("url", "")
                    domain = urlparse(url).netloc.lower().removeprefix("www.")

                    results.append(
                        WebSearchResult(
                            url=url,
                            title=item.get("title", "Search Result"),
                            content=item.get("content", ""),
                            domain=domain,
                            score=float(item.get("score", 0.0)),
                            raw_payload=item,
                        )
                    )
                return results
        except Exception as exc:
            logger.warning("Tavily search exception: %s", exc)
            return []
