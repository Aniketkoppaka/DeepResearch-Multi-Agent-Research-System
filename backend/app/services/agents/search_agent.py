"""
Search Researcher Agent.
Formulates targeted search queries and executes dual retrieval across Qdrant RAG and Web sources.
"""


import json
import logging
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field

from app.core.llm_gateway import LiteLLMGateway, get_litellm_gateway
from app.services.agents.state import ResearchPlan
from app.services.retrieval.base import SearchResultItem
from app.services.retrieval.hybrid_search import HybridSearchService
from app.services.web_search.base import WebSearchResult
from app.services.web_search.search_service import WebSearchEngine

logger = logging.getLogger(__name__)


class SearchExecutionResult(BaseModel):
    queries_executed: List[str] = Field(default_factory=list)
    document_chunks: List[SearchResultItem] = Field(default_factory=list)
    web_results: List[WebSearchResult] = Field(default_factory=list)


class SearchAgent:
    def __init__(
        self,
        hybrid_search: HybridSearchService,
        web_search: WebSearchEngine,
        llm_gateway: Optional[LiteLLMGateway] = None,
    ) -> None:
        self.hybrid_search = hybrid_search
        self.web_search = web_search
        self.llm_gateway = llm_gateway or get_litellm_gateway()

    async def formulate_queries(
        self,
        plan: ResearchPlan,
        iteration: int = 1,
        unresolved_questions: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Dynamically generates 2-4 search queries tailored to unresolved research questions.
        """
        questions = unresolved_questions or plan.research_questions
        strategy = plan.search_strategy.get("keywords", [])

        system_prompt = (
            "You are a search query formulation specialist. "
            "Generate 2-3 precise, keyword-rich search queries to investigate research questions."
        )


        user_content = (
            f"Research Objectives: {plan.objectives}\n"
            f"Target Questions: {questions}\n"
            f"Known Strategy Keywords: {strategy}\n"
            f"Current Iteration: {iteration}\n"
            "\nOutput ONLY a JSON array of query strings, e.g. [\"query 1\", \"query 2\"]"
        )

        try:
            res = await self.llm_gateway.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ]
            )
            content = res.content.strip()
            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            queries = json.loads(content)
            if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
                return queries[:4]
        except Exception as exc:
            logger.warning("Query formulation fallback triggered: %s", exc)

        # Heuristic fallback
        base_queries = strategy if strategy else [plan.title]
        return [f"{q} analysis" for q in base_queries[:3]]

    async def execute_search(
        self,
        workspace_id: uuid.UUID,
        queries: List[str],
        allowed_domains: Optional[List[str]] = None,
        max_results_per_query: int = 3,
    ) -> SearchExecutionResult:
        """
        Executes parallel hybrid document RAG search and web search across generated queries.
        """
        doc_chunks: List[SearchResultItem] = []
        web_results: List[WebSearchResult] = []

        for q in queries:
            # 1. Internal Document Retrieval (Qdrant RRF)
            try:
                chunks = await self.hybrid_search.search(
                    query=q,
                    workspace_id=workspace_id,
                    limit=max_results_per_query,
                )
                doc_chunks.extend(chunks)
            except Exception as e:
                logger.warning("Internal hybrid search error for '%s': %s", q, e)

            # 2. External Web Search (Tavily / DuckDuckGo)
            try:
                web_res = await self.web_search.search(
                    query=q,
                    max_results=max_results_per_query,
                    allowed_domains=allowed_domains,
                )
                web_results.extend(web_res)
            except Exception as e:
                logger.warning("Web search error for '%s': %s", q, e)

        return SearchExecutionResult(
            queries_executed=queries,
            document_chunks=doc_chunks,
            web_results=web_results,
        )
