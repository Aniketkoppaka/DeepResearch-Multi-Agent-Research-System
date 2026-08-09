import uuid
from typing import List
from fastapi import HTTPException, status
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse


class WorkspaceService:
    def __init__(self, workspace_repo: WorkspaceRepository) -> None:
        self.workspace_repo = workspace_repo

    async def create_workspace(
        self, user_id: uuid.UUID, data: WorkspaceCreate
    ) -> WorkspaceResponse:
        workspace = await self.workspace_repo.create(
            user_id=user_id,
            title=data.title,
            description=data.description,
            research_mode=data.research_mode,
        )
        return WorkspaceResponse.model_validate(workspace)

    async def get_workspace(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID
    ) -> WorkspaceResponse:
        workspace = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        return WorkspaceResponse.model_validate(workspace)

    async def list_workspaces(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[WorkspaceResponse]:
        workspaces = await self.workspace_repo.list_by_user(user_id, skip, limit)
        return [WorkspaceResponse.model_validate(w) for w in workspaces]

    async def update_workspace(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID, data: WorkspaceUpdate
    ) -> WorkspaceResponse:
        workspace = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        updated = await self.workspace_repo.update(
            workspace=workspace,
            title=data.title,
            description=data.description,
            research_mode=data.research_mode,
            status=data.status,
        )
        return WorkspaceResponse.model_validate(updated)

    async def delete_workspace(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        workspace = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        return await self.workspace_repo.delete(workspace)
