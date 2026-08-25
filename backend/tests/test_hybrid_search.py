"""
Unit and integration tests for HybridSearchService and Reciprocal Rank Fusion.
"""

import uuid
from unittest.mock import AsyncMock
import pytest
from httpx import AsyncClient

from app.core.llm_gateway import LiteLLMGateway
from app.services.retrieval.hybrid_search import HybridSearchService
from app.services.retrieval.vector_store import VectorStoreService


class MockPoint:
    def __init__(self, pt_id, score, payload):
        self.id = pt_id
        self.score = score
        self.payload = payload


@pytest.mark.asyncio
async def test_hybrid_search_rrf_scoring():
    mock_vector_store = AsyncMock(spec=VectorStoreService)
    mock_llm_gateway = AsyncMock(spec=LiteLLMGateway)

    ws_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    chunk1_id = uuid.uuid4()
    chunk2_id = uuid.uuid4()

    mock_llm_gateway.generate_embeddings.return_value = [[0.1] * 1536]

    # Dense returns chunk 1 then chunk 2
    mock_vector_store.search_dense.return_value = [
        MockPoint(
            str(chunk1_id),
            0.95,
            {
                "chunk_id": str(chunk1_id),
                "document_id": str(doc_id),
                "workspace_id": str(ws_id),
                "chunk_index": 0,
                "content": "Deep research systems",
                "section_heading": "Introduction",
                "page_number": 1,
            },
        ),
        MockPoint(
            str(chunk2_id),
            0.85,
            {
                "chunk_id": str(chunk2_id),
                "document_id": str(doc_id),
                "workspace_id": str(ws_id),
                "chunk_index": 1,
                "content": "Sparse vector encoding",
                "section_heading": "Methods",
                "page_number": 2,
            },
        ),
    ]

    # Sparse returns chunk 2 then chunk 1
    mock_vector_store.search_sparse.return_value = [
        MockPoint(
            str(chunk2_id),
            1.5,
            {
                "chunk_id": str(chunk2_id),
                "document_id": str(doc_id),
                "workspace_id": str(ws_id),
                "chunk_index": 1,
                "content": "Sparse vector encoding",
                "section_heading": "Methods",
                "page_number": 2,
            },
        ),
        MockPoint(
            str(chunk1_id),
            0.8,
            {
                "chunk_id": str(chunk1_id),
                "document_id": str(doc_id),
                "workspace_id": str(ws_id),
                "chunk_index": 0,
                "content": "Deep research systems",
                "section_heading": "Introduction",
                "page_number": 1,
            },
        ),
    ]

    search_service = HybridSearchService(
        vector_store=mock_vector_store,
        llm_gateway=mock_llm_gateway,
        dense_weight=0.7,
        sparse_weight=0.3,
    )

    results = await search_service.search("research systems", workspace_id=ws_id, limit=5)
    assert len(results) == 2
    # Both chunks returned, with calculated RRF scores
    assert results[0].score > 0
    assert results[1].score > 0
    assert results[0].chunk_id in (chunk1_id, chunk2_id)


@pytest.mark.asyncio
async def test_search_api_workspace_idor_protection(client: AsyncClient, test_user):
    random_ws_id = uuid.uuid4()
    res = await client.post(
        f"/api/v1/workspaces/{random_ws_id}/search",
        json={"query": "test query", "limit": 10},
    )

    # Unauthorized or Not Found
    assert res.status_code in (401, 404)
