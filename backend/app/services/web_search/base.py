"""
Base definitions and protocols for web search providers.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class WebSearchResult:
    url: str
    title: str
    content: str
    domain: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[datetime] = None
    score: float = 0.0
    raw_payload: Dict[str, Any] = field(default_factory=dict)


class SearchProvider(Protocol):
    async def search(
        self,
        query: str,
        max_results: int = 5,
        allowed_domains: Optional[List[str]] = None,
    ) -> List[WebSearchResult]:
        ...
