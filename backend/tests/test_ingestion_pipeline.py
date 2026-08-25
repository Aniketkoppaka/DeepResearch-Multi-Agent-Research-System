"""
Integration tests for document ingestion pipeline, ARQ tasks, state transitions, re-ingestion, and IDOR protection.
"""

import os
import tempfile
import pytest

from app.db.models.document import Document
from app.db.models.workspace import Workspace
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.ingestion_service import IngestionService


@pytest.mark.asyncio
async def test_ingestion_pipeline_end_to_end(db_session, test_user):
    # 1. Setup workspace & document
    ws = Workspace(user_id=test_user.id, title="Test WS", research_mode="Deep")
    db_session.add(ws)
    await db_session.commit()
    await db_session.refresh(ws)

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
        f.write("# Introduction\n\nThis is a sample research document text block.\n\n## Section 2\n\nMore detailed analysis.")
        temp_path = f.name

    doc = Document(
        workspace_id=ws.id,
        filename="sample.txt",
        mime_type="text/plain",
        file_size=100,
        storage_key=temp_path,
        status="uploaded",
    )
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)

    try:
        # 2. Execute ingestion service
        doc_repo = DocumentRepository(db_session)
        chunk_repo = DocumentChunkRepository(db_session)
        ingest_service = IngestionService(doc_repo, chunk_repo)

        success = await ingest_service.ingest_document(doc.id, ws.id)
        assert success is True

        # Refresh document
        await db_session.refresh(doc)
        assert doc.status == "processed"
        assert doc.chunk_count > 0
        assert doc.error_message is None

        # Verify chunks persisted in DB
        chunks = await chunk_repo.get_chunks_by_document(doc.id, ws.id)
        assert len(chunks) == doc.chunk_count
        assert chunks[0].estimated_tokens > 0
        assert chunks[0].document_id == doc.id

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@pytest.mark.asyncio
async def test_reingestion_failure_preserves_previous_chunks(db_session, test_user):
    ws = Workspace(user_id=test_user.id, title="Reingest WS", research_mode="Deep")
    db_session.add(ws)
    await db_session.commit()

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
        f.write("Original content for chunking.")
        valid_path = f.name

    doc = Document(
        workspace_id=ws.id,
        filename="valid.txt",
        mime_type="text/plain",
        file_size=50,
        storage_key=valid_path,
        status="uploaded",
    )
    db_session.add(doc)
    await db_session.commit()

    doc_repo = DocumentRepository(db_session)
    chunk_repo = DocumentChunkRepository(db_session)
    service = IngestionService(doc_repo, chunk_repo)

    # Initial successful ingestion
    await service.ingest_document(doc.id, ws.id)
    await db_session.refresh(doc)
    assert doc.status == "processed"
    original_chunks = await chunk_repo.get_chunks_by_document(doc.id, ws.id)
    assert len(original_chunks) == 1

    # Simulate file missing during re-ingestion
    os.remove(valid_path)
    # Re-ingest
    success = await service.ingest_document(doc.id, ws.id)
    assert success is False

    await db_session.refresh(doc)
    assert doc.status == "failed"
    assert doc.error_message is not None
    # Previous chunks MUST be preserved untouched!
    preserved_chunks = await chunk_repo.get_chunks_by_document(doc.id, ws.id)
    assert len(preserved_chunks) == 1
    assert preserved_chunks[0].content == original_chunks[0].content


@pytest.mark.asyncio
async def test_concurrent_worker_claim(db_session, test_user):
    ws = Workspace(user_id=test_user.id, title="Claim WS", research_mode="Deep")
    db_session.add(ws)
    await db_session.commit()

    doc = Document(
        workspace_id=ws.id,
        filename="claim.txt",
        mime_type="text/plain",
        file_size=10,
        storage_key="nonexistent.txt",
        status="uploaded",
    )
    db_session.add(doc)
    await db_session.commit()

    doc_repo = DocumentRepository(db_session)
    # Worker 1 claims
    c1 = await doc_repo.claim_for_processing(doc.id)
    assert c1 is True

    # Worker 2 attempts claim while status is processing
    c2 = await doc_repo.claim_for_processing(doc.id)
    assert c2 is False
