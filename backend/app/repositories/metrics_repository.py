"""
Repository for WorkspaceMetric database operations.
"""

from typing import Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.metrics import WorkspaceMetric


class MetricsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, metric: WorkspaceMetric) -> WorkspaceMetric:
        self.session.add(metric)
        await self.session.commit()
        await self.session.refresh(metric)
        return metric

    async def get_latest_by_workspace(
        self, workspace_id: uuid.UUID
    ) -> Optional[WorkspaceMetric]:
        stmt = (
            select(WorkspaceMetric)
            .where(WorkspaceMetric.workspace_id == workspace_id)
            .order_by(WorkspaceMetric.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
