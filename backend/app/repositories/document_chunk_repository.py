import uuid
from typing import List
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.document_chunk import DocumentChunk
from app.services.ingestion.base import ProcessedChunk


class DocumentChunkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def bulk_create(
        self,
        document_id: uuid.UUID,
        workspace_id: uuid.UUID,
        chunks: List[ProcessedChunk],
    ) -> List[DocumentChunk]:
        db_chunks: List[DocumentChunk] = []
        for c in chunks:
            chunk = DocumentChunk(
                document_id=document_id,
                workspace_id=workspace_id,
                chunk_index=c.chunk_index,
                content=c.content,
                estimated_tokens=c.estimated_tokens,
                section_heading=c.section_heading,
                page_number=c.page_number,
                metadata_json=c.metadata_json,
            )
            db_chunks.append(chunk)
            self.session.add(chunk)

        await self.session.flush()
        return db_chunks

    async def get_chunks_by_document(
        self, document_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> List[DocumentChunk]:
        stmt = (
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id,
                DocumentChunk.workspace_id == workspace_id,
            )
            .order_by(DocumentChunk.chunk_index.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_document(self, document_id: uuid.UUID) -> int:
        stmt = delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        result = await self.session.execute(stmt)
        return result.rowcount or 0
