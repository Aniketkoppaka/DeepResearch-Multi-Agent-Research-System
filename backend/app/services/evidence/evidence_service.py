"""
Evidence Knowledge Graph Service coordinating EKG creation, credibility scoring, and web ingestion.
"""

import logging
from typing import List, Optional
import uuid

from fastapi import HTTPException, status

from app.db.models.evidence import EvidenceEdge, EvidenceNode, EvidenceSource
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.evidence import (
    EvidenceEdgeCreate,
    EvidenceGraphResponse,
    EvidenceNodeCreate,
    EvidenceSourceCreate,
)
from app.services.evidence.credibility import calculate_credibility_score
from app.services.web_search.base import WebSearchResult
from app.services.web_search.search_service import WebSearchEngine

logger = logging.getLogger(__name__)


class EvidenceService:
    def __init__(
        self,
        evidence_repo: EvidenceRepository,
        workspace_repo: WorkspaceRepository,
        web_search_engine: Optional[WebSearchEngine] = None,
    ) -> None:
        self.evidence_repo = evidence_repo
        self.workspace_repo = workspace_repo
        self.web_search_engine = web_search_engine or WebSearchEngine()

    async def create_source(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        data: EvidenceSourceCreate,
    ) -> EvidenceSource:
        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

        credibility, breakdown = calculate_credibility_score(
            url=data.url,
            domain=data.domain,
            author=data.author,
            publication_date=data.publication_date,
        )

        source = EvidenceSource(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            url=data.url,
            title=data.title,
            domain=data.domain,
            author=data.author,
            publication_date=data.publication_date,
            credibility_score=credibility,
            credibility_breakdown=breakdown,
        )
        return await self.evidence_repo.create_source(source)

    async def create_node(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        data: EvidenceNodeCreate,
    ) -> EvidenceNode:
        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

        source = await self.evidence_repo.get_source_by_id(data.source_id, workspace_id)
        if not source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence source not found in workspace",
            )

        node = EvidenceNode(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            source_id=data.source_id,
            claim_text=data.claim_text,
            claim_type=data.claim_type.value,
            confidence_score=data.confidence_score,
            extracted_by_agent=data.extracted_by_agent,
            supporting_reasoning=data.supporting_reasoning,
            entities=data.entities,
        )
        return await self.evidence_repo.create_node(node)

    async def create_edge(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        data: EvidenceEdgeCreate,
    ) -> EvidenceEdge:
        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

        source_node = await self.evidence_repo.get_node_by_id(data.source_node_id, workspace_id)
        target_node = await self.evidence_repo.get_node_by_id(data.target_node_id, workspace_id)
        if not source_node or not target_node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source or Target evidence node not found in workspace",
            )

        edge = EvidenceEdge(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            source_node_id=data.source_node_id,
            target_node_id=data.target_node_id,
            relationship_type=data.relationship_type.value,
            confidence=data.confidence,
            reasoning=data.reasoning,
        )
        return await self.evidence_repo.create_edge(edge)

    async def get_graph(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID
    ) -> EvidenceGraphResponse:
        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

        sources = await self.evidence_repo.list_sources(workspace_id)
        nodes = await self.evidence_repo.list_nodes(workspace_id)
        edges = await self.evidence_repo.list_edges(workspace_id)

        from app.schemas.evidence import (
            EvidenceEdgeResponse,
            EvidenceNodeResponse,
            EvidenceSourceResponse,
        )

        return EvidenceGraphResponse(
            workspace_id=workspace_id,
            sources=[EvidenceSourceResponse.model_validate(s) for s in sources],
            nodes=[EvidenceNodeResponse.model_validate(n) for n in nodes],
            edges=[EvidenceEdgeResponse.model_validate(e) for e in edges],
            total_nodes=len(nodes),
            total_edges=len(edges),
        )

    async def search_web_and_index(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        query: str,
        max_results: int = 5,
        allowed_domains: Optional[List[str]] = None,
    ) -> List[EvidenceSource]:
        """
        Execute web search, calculate credibility score, and store as EvidenceSource.
        """

        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

        results: List[WebSearchResult] = await self.web_search_engine.search(
            query=query,
            max_results=max_results,
            allowed_domains=allowed_domains,
        )

        created_sources: List[EvidenceSource] = []
        for r in results:
            credibility, breakdown = calculate_credibility_score(
                url=r.url,
                domain=r.domain,
                author=r.author,
                publication_date=r.publication_date,
            )
            source = EvidenceSource(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                url=r.url,
                title=r.title or "Web Search Source",
                domain=r.domain,
                author=r.author,
                publication_date=r.publication_date,
                credibility_score=credibility,
                credibility_breakdown=breakdown,
            )
            saved = await self.evidence_repo.create_source(source)
            created_sources.append(saved)

        return created_sources
