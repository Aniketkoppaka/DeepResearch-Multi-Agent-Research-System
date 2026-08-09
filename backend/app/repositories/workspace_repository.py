import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.workspace import Workspace, ResearchMode, WorkspaceStatus


class WorkspaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        user_id: uuid.UUID,
        title: str,
        description: Optional[str] = None,
        research_mode: ResearchMode = ResearchMode.DEEP,
    ) -> Workspace:
        workspace = Workspace(
            user_id=user_id,
            title=title,
            description=description,
            research_mode=research_mode,
        )
        self.session.add(workspace)
        await self.session.commit()
        await self.session.refresh(workspace)
        return workspace

    async def get_by_id_and_user(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Workspace]:
        stmt = select(Workspace).where(
            Workspace.id == workspace_id, Workspace.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Workspace]:
        stmt = (
            select(Workspace)
            .where(Workspace.user_id == user_id)
            .order_by(Workspace.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        workspace: Workspace,
        title: Optional[str] = None,
        description: Optional[str] = None,
        research_mode: Optional[ResearchMode] = None,
        status: Optional[WorkspaceStatus] = None,
    ) -> Workspace:
        if title is not None:
            workspace.title = title
        if description is not None:
            workspace.description = description
        if research_mode is not None:
            workspace.research_mode = research_mode
        if status is not None:
            workspace.status = status
        await self.session.commit()
        await self.session.refresh(workspace)
        return workspace

    async def delete(self, workspace: Workspace) -> bool:
        await self.session.delete(workspace)
        await self.session.commit()
        return True
