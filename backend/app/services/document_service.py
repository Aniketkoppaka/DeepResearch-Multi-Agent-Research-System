import os
import re
import uuid
from typing import List, Optional

from fastapi import HTTPException, UploadFile, status

from app.repositories.document_repository import DocumentRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.document import DocumentResponse
from app.workers.ingestion_worker import enqueue_ingestion_job

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
ALLOWED_MIME_TYPES = {
    "application/pdf": [b"%PDF-"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
        b"PK\x03\x04",
        b"PK\x05\x06",
        b"PK\x07\x08",
    ],
    "text/plain": [],
    "text/markdown": [],
}


def sanitize_filename(filename: Optional[str]) -> str:
    if not filename:
        return "uploaded_file"
    base = os.path.basename(filename)
    return re.sub(r"[^\w\.\-]", "_", base)


class DocumentService:
    def __init__(
        self,
        document_repo: DocumentRepository,
        workspace_repo: WorkspaceRepository,
        upload_dir: str = "uploads",
    ) -> None:
        self.document_repo = document_repo
        self.workspace_repo = workspace_repo
        self.upload_dir = upload_dir

    async def upload_document(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        file: UploadFile,
    ) -> DocumentResponse:
        # 1. Ownership check
        workspace = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )

        # 2. Filename & extension sanitization
        filename = sanitize_filename(file.filename)

        # 3. Read content and validate size
        contents = await file.read()
        file_size = len(contents)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"File size exceeds maximum allowed limit of"
                    f" {MAX_FILE_SIZE // (1024 * 1024)}MB"
                ),
            )
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        # 4. MIME type & Magic-byte signature validation
        declared_mime = file.content_type or ""
        if declared_mime not in ALLOWED_MIME_TYPES:
            # Fallback check by file extension for markdown files (.md)
            if filename.endswith(".md"):
                declared_mime = "text/markdown"
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type '{declared_mime}'. Allowed: PDF, DOCX, TXT, MD",
                )

        # Verify magic byte signatures
        signatures = ALLOWED_MIME_TYPES.get(declared_mime, [])
        if signatures:
            matched = any(contents.startswith(sig) for sig in signatures)
            if not matched:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File content header does not match the declared MIME type signature",
                )

        # 5. Safe Storage key generation
        document_id = uuid.uuid4()
        ext = os.path.splitext(filename)[1]
        storage_key = os.path.join(
            self.upload_dir, str(workspace_id), f"{document_id}{ext}"
        ).replace("\\", "/")

        # Save to filesystem
        os.makedirs(os.path.dirname(storage_key), exist_ok=True)
        with open(storage_key, "wb") as f:
            f.write(contents)

        # 6. Database creation (status='uploaded')
        doc = await self.document_repo.create(
            workspace_id=workspace_id,
            filename=filename,
            mime_type=declared_mime,
            file_size=file_size,
            storage_key=storage_key,
            status="uploaded",
        )

        # 7. Post-commit ARQ background job enqueueing
        await enqueue_ingestion_job(doc.id, workspace_id)

        return DocumentResponse.model_validate(doc)

    async def trigger_ingestion(
        self, workspace_id: uuid.UUID, document_id: uuid.UUID, user_id: uuid.UUID
    ) -> DocumentResponse:
        """Manual endpoint to re-trigger ingestion for document."""
        workspace = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        doc = await self.document_repo.get_by_id(document_id)
        if not doc or doc.workspace_id != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found in workspace",
            )

        if doc.status == "processing":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document is currently processing. Concurrent ingestion is blocked.",
            )

        # Enqueue job to Redis/ARQ
        await enqueue_ingestion_job(doc.id, workspace_id)
        return DocumentResponse.model_validate(doc)

    async def list_documents(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID
    ) -> List[DocumentResponse]:
        workspace = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        documents = await self.document_repo.list_by_workspace(workspace_id)
        return [DocumentResponse.model_validate(d) for d in documents]

    async def delete_document(
        self, workspace_id: uuid.UUID, document_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        workspace = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        document = await self.document_repo.get_by_id(document_id)
        if not document or document.workspace_id != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found in workspace",
            )
        # Remove file if exists
        if os.path.exists(document.storage_key):
            try:
                os.remove(document.storage_key)
            except OSError:
                pass
        return await self.document_repo.delete(document)
