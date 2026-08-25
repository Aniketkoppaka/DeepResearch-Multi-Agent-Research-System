import uuid
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.v1.deps import (
    get_current_user,
    get_document_chunk_repository,
    get_document_service,
    get_workspace_repository,
)
from app.db.models.user import User
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.document import DocumentResponse
from app.schemas.document_chunk import DocumentChunkResponse
from app.services.document_service import DocumentService

router = APIRouter()


@router.post(
    "/{workspace_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    workspace_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    return await document_service.upload_document(workspace_id, current_user.id, file)


@router.post(
    "/{workspace_id}/documents/{document_id}/ingest",
    response_model=DocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_ingestion(
    workspace_id: uuid.UUID,
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """Manual endpoint to re-trigger ingestion for an uploaded/failed document."""
    return await document_service.trigger_ingestion(
        workspace_id, document_id, current_user.id
    )


@router.get(
    "/{workspace_id}/documents/{document_id}/chunks",
    response_model=List[DocumentChunkResponse],
)
async def get_document_chunks(
    workspace_id: uuid.UUID,
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    chunk_repo: DocumentChunkRepository = Depends(get_document_chunk_repository),
) -> List[DocumentChunkResponse]:
    """Retrieve processed semantic chunks for document (IDOR protected)."""
    workspace = await workspace_repo.get_by_id_and_user(workspace_id, current_user.id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    chunks = await chunk_repo.get_chunks_by_document(document_id, workspace_id)
    return [DocumentChunkResponse.model_validate(c) for c in chunks]


@router.get("/{workspace_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> List[DocumentResponse]:
    return await document_service.list_documents(workspace_id, current_user.id)


@router.delete("/{workspace_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    workspace_id: uuid.UUID,
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> None:
    await document_service.delete_document(workspace_id, document_id, current_user.id)
