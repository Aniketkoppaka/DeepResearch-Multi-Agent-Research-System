"""
DuckDuckGo Search Provider implementation using lightweight async HTML/JSON endpoint.
Provides keyless zero-config web search fallback.
"""

import logging
import re
from typing import List, Optional
from urllib.parse import urlparse

import httpx

from app.services.web_search.base import WebSearchResult

logger = logging.getLogger(__name__)


class DuckDuckGoProvider:
    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout
        self.endpoint = "https://html.duckduckgo.com/html/"

    async def search(
        self,
        query: str,
        max_results: int = 5,
        allowed_domains: Optional[List[str]] = None,
    ) -> List[WebSearchResult]:
        if not query.strip():
            return []

        formatted_query = query
        if allowed_domains:
            domain_filter = " OR ".join(f"site:{d}" for d in allowed_domains)
            formatted_query = f"{query} ({domain_filter})"

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                res = await client.post(
                    self.endpoint,
                    data={"q": formatted_query, "b": ""},
                    headers=headers,
                )
                if res.status_code != 200:
                    logger.warning(
                        "DuckDuckGo search returned status %d", res.status_code
                    )
                    return []

                return self._parse_html(res.text, max_results)
        except Exception as exc:
            logger.warning("DuckDuckGo search error: %s", exc)
            return []

    def _parse_html(self, html: str, max_results: int) -> List[WebSearchResult]:
        results: List[WebSearchResult] = []
        # Pattern to capture result links and snippets from DDG HTML
        blocks = re.findall(r'<div class="result__body">([\s\S]*?)</div>\s*</div>', html)

        for block in blocks:
            if len(results) >= max_results:
                break

            title_match = re.search(r'<a class="result__snippet[^>]*>([\s\S]*?)</a>', block)
            if not title_match:
                title_match = re.search(r'<a class="result__url[^>]*>([\s\S]*?)</a>', block)

            url_match = re.search(r'<a class="result__url"[^>]*href="([^"]+)"', block)
            snippet_match = re.search(r'<a class="result__snippet[^>]*>([\s\S]*?)</a>', block)

            raw_url = url_match.group(1) if url_match else ""
            if "uddg=" in raw_url:
                # Extract actual decoded redirect URL
                import urllib.parse
                m = re.search(r"uddg=([^&]+)", raw_url)
                if m:
                    raw_url = urllib.parse.unquote(m.group(1))

            if not raw_url.startswith("http"):
                continue

            raw_title = title_match.group(1) if title_match else raw_url
            raw_snippet = snippet_match.group(1) if snippet_match else ""

            clean_title = re.sub(r"<[^>]+>", "", raw_title).strip()
            clean_snippet = re.sub(r"<[^>]+>", "", raw_snippet).strip()
            domain = urlparse(raw_url).netloc.lower().removeprefix("www.")


            results.append(
                WebSearchResult(
                    url=raw_url,
                    title=clean_title or "Web Search Result",
                    content=clean_snippet,
                    domain=domain,
                )
            )

        return results
