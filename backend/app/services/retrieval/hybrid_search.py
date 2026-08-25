"""
Hybrid Retrieval and Reciprocal Rank Fusion (RRF) Service.
Executes parallel dense and sparse searches and fuses ranks with configured weights.
"""

import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional


from app.core.config import settings
from app.core.llm_gateway import LiteLLMGateway
from app.services.retrieval.base import SearchResultItem
from app.services.retrieval.sparse_encoder import SparseEncoder
from app.services.retrieval.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class HybridSearchService:
    def __init__(
        self,
        vector_store: VectorStoreService,
        llm_gateway: LiteLLMGateway,
        sparse_encoder: Optional[SparseEncoder] = None,
        dense_weight: Optional[float] = None,
        sparse_weight: Optional[float] = None,
        rrf_k: Optional[int] = None,
    ) -> None:
        self.vector_store = vector_store
        self.llm_gateway = llm_gateway
        self.sparse_encoder = sparse_encoder or SparseEncoder()
        self.dense_weight = (
            dense_weight if dense_weight is not None else settings.HYBRID_SEARCH_DENSE_WEIGHT
        )
        self.sparse_weight = (
            sparse_weight if sparse_weight is not None else settings.HYBRID_SEARCH_SPARSE_WEIGHT
        )
        self.rrf_k = rrf_k or settings.RRF_K_CONSTANT

    async def search(
        self,
        query: str,
        workspace_id: uuid.UUID,
        document_ids: Optional[List[uuid.UUID]] = None,
        limit: int = 10,
    ) -> List[SearchResultItem]:
        """
        Execute parallel dense & sparse search and fuse results with Reciprocal Rank Fusion.
        """
        if not query.strip():
            return []

        # 1. Encode query (dense embedding via LiteLLM + sparse representation)
        dense_embedding_task = self.llm_gateway.generate_embeddings([query])
        sparse_query = self.sparse_encoder.encode(query)

        try:
            dense_embeddings = await dense_embedding_task
            dense_query = dense_embeddings[0] if dense_embeddings else []
        except Exception as exc:
            logger.warning("Dense embedding generation failed during search: %s", exc)
            dense_query = []

        # 2. Execute parallel vector store queries
        tasks = []
        if dense_query:
            tasks.append(
                self.vector_store.search_dense(
                    dense_query=dense_query,
                    workspace_id=workspace_id,
                    document_ids=document_ids,
                    limit=limit * 2,
                )
            )
        else:
            tasks.append(asyncio.sleep(0, result=[]))

        if sparse_query.indices:
            tasks.append(
                self.vector_store.search_sparse(
                    sparse_query=sparse_query,
                    workspace_id=workspace_id,
                    document_ids=document_ids,
                    limit=limit * 2,
                )
            )
        else:
            tasks.append(asyncio.sleep(0, result=[]))

        dense_points, sparse_points = await asyncio.gather(*tasks)

        # 3. Reciprocal Rank Fusion (RRF)
        return self._reciprocal_rank_fusion(
            dense_points=dense_points,
            sparse_points=sparse_points,
            limit=limit,
        )

    def _reciprocal_rank_fusion(
        self,
        dense_points: List[Any],
        sparse_points: List[Any],
        limit: int = 10,
    ) -> List[SearchResultItem]:
        """
        Combine dense and sparse candidate rankings:
        Score(d) = dense_weight * (1 / (K + rank_dense)) + sparse_weight * (1 / (K + rank_sparse))
        """
        scores: Dict[str, float] = {}
        payload_map: Dict[str, Dict[str, Any]] = {}


        # Process dense ranks
        for rank, pt in enumerate(dense_points, start=1):
            pt_id = str(pt.id)
            rrf_score = self.dense_weight * (1.0 / (self.rrf_k + rank))
            scores[pt_id] = scores.get(pt_id, 0.0) + rrf_score
            if pt_id not in payload_map:
                payload_map[pt_id] = pt.payload or {}

        # Process sparse ranks
        for rank, pt in enumerate(sparse_points, start=1):
            pt_id = str(pt.id)
            rrf_score = self.sparse_weight * (1.0 / (self.rrf_k + rank))
            scores[pt_id] = scores.get(pt_id, 0.0) + rrf_score
            if pt_id not in payload_map:
                payload_map[pt_id] = pt.payload or {}

        # Sort combined results by fused score descending
        sorted_results = sorted(scores.items(), key=lambda item: item[1], reverse=True)[
            :limit
        ]

        results: List[SearchResultItem] = []
        for pt_id, fused_score in sorted_results:
            payload = payload_map.get(pt_id, {})
            try:
                results.append(
                    SearchResultItem(
                        chunk_id=uuid.UUID(payload.get("chunk_id", pt_id)),
                        document_id=uuid.UUID(payload.get("document_id", "")),
                        workspace_id=uuid.UUID(payload.get("workspace_id", "")),
                        chunk_index=int(payload.get("chunk_index", 0)),
                        content=str(payload.get("content", "")),
                        score=round(fused_score, 6),
                        section_heading=payload.get("section_heading"),
                        page_number=payload.get("page_number"),
                        metadata_json=payload.get("metadata_json", {}),
                    )
                )
            except (ValueError, TypeError) as err:
                logger.warning("Error unpacking search payload for %s: %s", pt_id, err)
                continue

        return results
