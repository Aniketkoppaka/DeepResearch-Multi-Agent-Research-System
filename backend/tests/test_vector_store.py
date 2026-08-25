"""
Unit tests for VectorStoreService managing Qdrant collection, upsert, and search.
"""

import uuid
from unittest.mock import AsyncMock
import pytest

from app.db.models.document_chunk import DocumentChunk
from app.services.retrieval.base import SparseVector
from app.services.retrieval.vector_store import VectorStoreService


@pytest.mark.asyncio
async def test_ensure_collection_exists_creates_when_missing():
    mock_client = AsyncMock()
    mock_collections = AsyncMock()
    mock_collections.collections = []
    mock_client.get_collections.return_value = mock_collections

    service = VectorStoreService(client=mock_client)
    await service.ensure_collection_exists()

    mock_client.create_collection.assert_called_once()
    assert mock_client.create_payload_index.call_count == 2


@pytest.mark.asyncio
async def test_upsert_chunks_success():
    mock_client = AsyncMock()
    mock_collections = AsyncMock()
    mock_collections.collections = []
    mock_client.get_collections.return_value = mock_collections

    service = VectorStoreService(client=mock_client)
    ws_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    chunk_id = uuid.uuid4()

    chunk = DocumentChunk(
        id=chunk_id,
        document_id=doc_id,
        workspace_id=ws_id,
        chunk_index=0,
        content="Test chunk content",
        estimated_tokens=10,
        section_heading="Intro",
        page_number=1,
        metadata_json={},
    )

    dense_emb = [[0.1] * 1536]
    sparse_vec = [SparseVector(indices=[10, 20], values=[0.8, 0.5])]

    success = await service.upsert_chunks(
        workspace_id=ws_id,
        document_id=doc_id,
        chunks=[chunk],
        dense_embeddings=dense_emb,
        sparse_vectors=sparse_vec,
    )
    assert success is True
    mock_client.upsert.assert_called_once()
