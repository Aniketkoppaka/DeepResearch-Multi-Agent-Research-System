"""
Evidence Repository handling PostgreSQL persistence for EKG sources, nodes, and relational edges.
"""

from typing import List, Optional
import uuid

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.evidence import EvidenceEdge, EvidenceNode, EvidenceSource


class EvidenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --- Evidence Sources ---
    async def create_source(self, source: EvidenceSource) -> EvidenceSource:
        self.session.add(source)
        await self.session.commit()
        await self.session.refresh(source)
        return source

    async def get_source_by_id(
        self, source_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Optional[EvidenceSource]:
        stmt = select(EvidenceSource).where(
            and_(
                EvidenceSource.id == source_id,
                EvidenceSource.workspace_id == workspace_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_sources(self, workspace_id: uuid.UUID) -> List[EvidenceSource]:
        stmt = (
            select(EvidenceSource)
            .where(EvidenceSource.workspace_id == workspace_id)
            .order_by(EvidenceSource.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --- Evidence Nodes ---
    async def create_node(self, node: EvidenceNode) -> EvidenceNode:
        self.session.add(node)
        await self.session.commit()
        await self.session.refresh(node)
        return node

    async def get_node_by_id(
        self, node_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Optional[EvidenceNode]:
        stmt = select(EvidenceNode).where(
            and_(
                EvidenceNode.id == node_id,
                EvidenceNode.workspace_id == workspace_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_nodes(self, workspace_id: uuid.UUID) -> List[EvidenceNode]:
        stmt = (
            select(EvidenceNode)
            .where(EvidenceNode.workspace_id == workspace_id)
            .order_by(EvidenceNode.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --- Evidence Edges ---
    async def create_edge(self, edge: EvidenceEdge) -> EvidenceEdge:
        self.session.add(edge)
        await self.session.commit()
        await self.session.refresh(edge)
        return edge

    async def list_edges(self, workspace_id: uuid.UUID) -> List[EvidenceEdge]:
        stmt = (
            select(EvidenceEdge)
            .where(EvidenceEdge.workspace_id == workspace_id)
            .order_by(EvidenceEdge.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_contradictions(self, workspace_id: uuid.UUID) -> List[EvidenceEdge]:
        stmt = (
            select(EvidenceEdge)
            .where(
                and_(
                    EvidenceEdge.workspace_id == workspace_id,
                    EvidenceEdge.relationship_type == "CONTRADICTS",
                )
            )
            .options(
                selectinload(EvidenceEdge.source_node),
                selectinload(EvidenceEdge.target_node),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
