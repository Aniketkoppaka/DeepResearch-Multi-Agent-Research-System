import uuid
from typing import Any, Dict, List, Optional


from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        workspace_id: uuid.UUID,
        filename: str,
        mime_type: str,
        file_size: int,
        storage_key: str,
        status: str = "uploaded",
    ) -> Document:
        doc = Document(
            workspace_id=workspace_id,
            filename=filename,
            mime_type=mime_type,
            file_size=file_size,
            storage_key=storage_key,
            status=status,
        )
        self.session.add(doc)
        await self.session.commit()
        await self.session.refresh(doc)
        return doc

    async def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        stmt = select(Document).where(Document.id == document_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_workspace(
        self, workspace_id: uuid.UUID
    ) -> List[Document]:
        stmt = (
            select(Document)
            .where(Document.workspace_id == workspace_id)
            .order_by(Document.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def claim_for_processing(self, document_id: uuid.UUID) -> bool:
        """Atomic claim transition to processing to prevent concurrent worker execution."""
        stmt = (
            update(Document)
            .where(Document.id == document_id, Document.status != "processing")
            .values(status="processing", error_message=None)
            .execution_options(synchronize_session=False)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return (result.rowcount or 0) > 0

    async def update_status(
        self,
        document_id: uuid.UUID,
        status: str,
        error_message: Optional[str] = None,
        chunk_count: Optional[int] = None,
    ) -> None:
        values: Dict[str, Any] = {"status": status}

        if error_message is not None or status == "processed":
            values["error_message"] = error_message
        if chunk_count is not None:
            values["chunk_count"] = chunk_count

        stmt = (
            update(Document)
            .where(Document.id == document_id)
            .values(**values)
            .execution_options(synchronize_session=False)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete(self, document: Document) -> bool:
        await self.session.delete(document)
        await self.session.commit()
        return True
