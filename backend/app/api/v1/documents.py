import uuid
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, status
from app.api.v1.deps import get_current_user, get_document_service
from app.db.models.user import User
from app.schemas.document import DocumentResponse
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
