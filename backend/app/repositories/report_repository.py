"""
Report Repository handling versioning and persistence for ReportVersion.
"""

from typing import List, Optional
import uuid

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.report import ReportVersion


class ReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_next_version_number(self, workspace_id: uuid.UUID) -> int:
        stmt = select(func.coalesce(func.max(ReportVersion.version_number), 0)).where(
            ReportVersion.workspace_id == workspace_id
        )
        result = await self.session.execute(stmt)
        max_ver = result.scalar_one()
        return max_ver + 1

    async def create(self, report: ReportVersion) -> ReportVersion:
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_by_id(
        self, report_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Optional[ReportVersion]:
        stmt = select(ReportVersion).where(
            and_(
                ReportVersion.id == report_id,
                ReportVersion.workspace_id == workspace_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_by_workspace(
        self, workspace_id: uuid.UUID
    ) -> Optional[ReportVersion]:
        stmt = (
            select(ReportVersion)
            .where(ReportVersion.workspace_id == workspace_id)
            .order_by(ReportVersion.version_number.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_workspace(
        self, workspace_id: uuid.UUID
    ) -> List[ReportVersion]:
        stmt = (
            select(ReportVersion)
            .where(ReportVersion.workspace_id == workspace_id)
            .order_by(ReportVersion.version_number.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
