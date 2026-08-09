import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from app.api.v1.deps import get_current_user, get_workspace_service
from app.db.models.user import User
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from app.services.workspace_service import WorkspaceService

router = APIRouter()


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
) -> WorkspaceResponse:
    return await workspace_service.create_workspace(current_user.id, data)


@router.get("", response_model=List[WorkspaceResponse])
async def list_workspaces(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
) -> List[WorkspaceResponse]:
    return await workspace_service.list_workspaces(current_user.id, skip, limit)


@router.get("/{id}", response_model=WorkspaceResponse)
async def get_workspace(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
) -> WorkspaceResponse:
    return await workspace_service.get_workspace(id, current_user.id)


@router.patch("/{id}", response_model=WorkspaceResponse)
async def update_workspace(
    id: uuid.UUID,
    data: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
) -> WorkspaceResponse:
    return await workspace_service.update_workspace(id, current_user.id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
) -> None:
    await workspace_service.delete_workspace(id, current_user.id)
