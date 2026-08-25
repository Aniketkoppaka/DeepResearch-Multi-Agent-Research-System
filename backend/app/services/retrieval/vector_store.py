"""
Qdrant Vector Store Service for managing dual named vectors (dense + sparse)
and payload filtering by workspace and document namespaces.
"""

import logging
import uuid
from typing import Any, List, Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import settings
from app.db.models.document_chunk import DocumentChunk
from app.services.retrieval.base import SparseVector

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self, client: Optional[AsyncQdrantClient] = None) -> None:
        self.client = client or AsyncQdrantClient(
            url=settings.QDRANT_URL, timeout=30.0
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    async def ensure_collection_exists(self) -> None:
        """
        Initialize Qdrant collection with named Dense vectors and Sparse vectors.
        """
        try:
            collections = await self.client.get_collections()
            existing_names = [c.name for c in collections.collections]

            if self.collection_name not in existing_names:
                logger.info(
                    "Creating Qdrant collection %s with dense (dim=%d) and sparse vectors...",
                    self.collection_name,
                    settings.EMBEDDING_DIMENSION,
                )
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={
                        "dense": qmodels.VectorParams(
                            size=settings.EMBEDDING_DIMENSION,
                            distance=qmodels.Distance.COSINE,
                        )
                    },
                    sparse_vectors_config={
                        "sparse": qmodels.SparseVectorParams(
                            index=qmodels.SparseIndexParams(
                                on_disk=False,
                            )
                        )
                    },
                )
                # Create payload keyword indexes for fast namespace filtering
                await self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="workspace_id",
                    field_schema=qmodels.PayloadSchemaType.KEYWORD,
                )
                await self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="document_id",
                    field_schema=qmodels.PayloadSchemaType.KEYWORD,
                )
                logger.info("Qdrant collection %s created successfully.", self.collection_name)
        except Exception as exc:
            logger.warning("Error ensuring Qdrant collection exists: %s", exc)

    async def upsert_chunks(
        self,
        workspace_id: uuid.UUID,
        document_id: uuid.UUID,
        chunks: List[DocumentChunk],
        dense_embeddings: List[List[float]],
        sparse_vectors: List[SparseVector],
    ) -> bool:
        """
        Upsert chunk points containing dense and sparse vectors and full payload metadata.
        """
        if not chunks:
            return True

        await self.ensure_collection_exists()

        points: List[qmodels.PointStruct] = []
        for chunk, dense, sparse in zip(chunks, dense_embeddings, sparse_vectors, strict=False):
            point = qmodels.PointStruct(
                id=str(chunk.id),
                vector={
                    "dense": dense,
                    "sparse": qmodels.SparseVector(
                        indices=sparse.indices,
                        values=sparse.values,
                    ),
                },
                payload={
                    "chunk_id": str(chunk.id),
                    "document_id": str(document_id),
                    "workspace_id": str(workspace_id),
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "estimated_tokens": chunk.estimated_tokens,
                    "section_heading": chunk.section_heading,
                    "page_number": chunk.page_number,
                    "metadata_json": chunk.metadata_json,
                },
            )
            points.append(point)

        try:
            await self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            logger.info(
                "Upserted %d vector points to Qdrant for document %s",
                len(points),
                document_id,
            )
            return True
        except Exception as exc:
            logger.error("Failed to upsert points to Qdrant: %s", exc)
            raise

    async def delete_by_document(self, document_id: uuid.UUID) -> bool:
        """
        Delete all vector points belonging to a document.
        """
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=qmodels.FilterSelector(
                    filter=qmodels.Filter(
                        must=[
                            qmodels.FieldCondition(
                                key="document_id",
                                match=qmodels.MatchValue(value=str(document_id)),
                            )
                        ]
                    )
                ),
            )
            return True
        except Exception as exc:
            logger.warning("Failed to delete points from Qdrant: %s", exc)
            return False

    async def search_dense(
        self,
        dense_query: List[float],
        workspace_id: uuid.UUID,
        document_ids: Optional[List[uuid.UUID]] = None,
        limit: int = 20,
    ) -> List[qmodels.ScoredPoint]:
        """
        Query Qdrant dense vector index with workspace filter.
        """
        must_conditions: List[Any] = [
            qmodels.FieldCondition(
                key="workspace_id",
                match=qmodels.MatchValue(value=str(workspace_id)),
            )
        ]
        if document_ids:
            must_conditions.append(
                qmodels.FieldCondition(
                    key="document_id",
                    match=qmodels.MatchAny(any=[str(d) for d in document_ids]),
                )
            )

        search_filter = qmodels.Filter(must=must_conditions)

        return await self.client.search(
            collection_name=self.collection_name,
            query_vector=qmodels.NamedVector(name="dense", vector=dense_query),
            query_filter=search_filter,
            limit=limit,
        )

    async def search_sparse(
        self,
        sparse_query: SparseVector,
        workspace_id: uuid.UUID,
        document_ids: Optional[List[uuid.UUID]] = None,
        limit: int = 20,
    ) -> List[qmodels.ScoredPoint]:
        """
        Query Qdrant sparse vector index with workspace filter.
        """
        if not sparse_query.indices:
            return []

        must_conditions: List[Any] = [
            qmodels.FieldCondition(
                key="workspace_id",
                match=qmodels.MatchValue(value=str(workspace_id)),
            )
        ]
        if document_ids:
            must_conditions.append(
                qmodels.FieldCondition(
                    key="document_id",
                    match=qmodels.MatchAny(any=[str(d) for d in document_ids]),
                )
            )

        search_filter = qmodels.Filter(must=must_conditions)

        return await self.client.search(
            collection_name=self.collection_name,
            query_vector=qmodels.NamedSparseVector(
                name="sparse",
                vector=qmodels.SparseVector(
                    indices=sparse_query.indices,
                    values=sparse_query.values,
                ),
            ),
            query_filter=search_filter,
            limit=limit,
        )
