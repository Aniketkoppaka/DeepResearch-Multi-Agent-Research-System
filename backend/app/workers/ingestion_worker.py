"""
ARQ Background Worker task definitions for async document ingestion.
Obtains its own AsyncSession and executes IngestionService.
"""

import logging
import uuid
from typing import Any, Dict

from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.ingestion_service import IngestionService
from app.services.retrieval.vector_store import VectorStoreService

logger = logging.getLogger("app.workers.ingestion")


async def enqueue_ingestion_job(document_id: uuid.UUID, workspace_id: uuid.UUID) -> bool:
    """Enqueue an ingestion background task to Redis/ARQ."""
    try:
        redis_settings = RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        redis = await create_pool(redis_settings)
        await redis.enqueue_job(
            "ingest_document_task",
            str(document_id),
            str(workspace_id),
            _job_id=f"ingest_{document_id}",
        )
        await redis.close()
        return True
    except Exception as e:
        logger.warning(
            "Failed to enqueue ARQ ingestion job for document %s: %s",
            document_id,
            str(e),
        )
        return False


async def ingest_document_task(
    ctx: Dict[str, Any], document_id_str: str, workspace_id_str: str
) -> bool:
    """ARQ Worker task executing document ingestion with its own DB session."""
    doc_id = uuid.UUID(document_id_str)
    ws_id = uuid.UUID(workspace_id_str)

    logger.info("ARQ Worker starting ingestion task for document %s", doc_id)

    async with AsyncSessionLocal() as session:
        doc_repo = DocumentRepository(session)
        chunk_repo = DocumentChunkRepository(session)
        vector_store = VectorStoreService()
        service = IngestionService(
            document_repo=doc_repo,
            chunk_repo=chunk_repo,
            vector_store=vector_store,
        )
        return await service.ingest_document(doc_id, ws_id)


class WorkerSettings:
    """ARQ Worker configuration for standalone worker processes."""

    functions = [ingest_document_task]
    redis_settings = RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    max_jobs = 10
    poll_delay = 0.5
