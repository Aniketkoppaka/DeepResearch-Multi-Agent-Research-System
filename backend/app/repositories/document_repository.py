import uuid
from typing import List, Optional
from sqlalchemy import select
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
    ) -> Document:
        doc = Document(
            workspace_id=workspace_id,
            filename=filename,
            mime_type=mime_type,
            file_size=file_size,
            storage_key=storage_key,
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

    async def delete(self, document: Document) -> bool:
        await self.session.delete(document)
        await self.session.commit()
        return True
