"""
Ingestion Service coordinating Loader -> Normalizer -> StructureDetector -> Chunker pipeline,
database transaction safety, vector embedding generation, Qdrant indexing, and chunk persistence.
"""

import logging
import os
import re
import uuid
from typing import Dict, List, Optional, Type

from app.core.llm_gateway import LiteLLMGateway, get_litellm_gateway
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.ingestion.base import (
    BaseChunker,
    BaseLoader,
    BaseNormalizer,
    BaseStructureDetector,
    ExtractedDocument,
    ProcessedChunk,
)
from app.services.ingestion.docx_loader import DocxLoader
from app.services.ingestion.markdown_loader import MarkdownLoader
from app.services.ingestion.normalizer import TextNormalizer
from app.services.ingestion.pdf_loader import PDFLoader
from app.services.ingestion.semantic_chunker import SemanticChunker
from app.services.ingestion.structure_detector import StructureDetector
from app.services.ingestion.txt_loader import TxtLoader
from app.services.retrieval.sparse_encoder import SparseEncoder
from app.services.retrieval.vector_store import VectorStoreService

logger = logging.getLogger("app.services.ingestion")

LOADERS: Dict[str, Type[BaseLoader]] = {
    "application/pdf": PDFLoader,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocxLoader,
    "text/plain": TxtLoader,
    "text/markdown": MarkdownLoader,
}


def sanitize_error_message(error: Exception) -> str:
    """Return a short, user-safe error message stripping paths and tracebacks."""
    raw = str(error)
    # Strip local path references
    clean = re.sub(r"[A-Za-z]:\\[^:\n\r]+", "[path]", raw)
    clean = re.sub(r"/[^\s:\n\r]+", "[path]", clean)

    if isinstance(error, FileNotFoundError):
        return "Document file storage missing or unreadable"
    if "PDF" in raw or "pdf" in raw:
        return "Failed to parse PDF document: Corrupted stream or invalid structure"
    if "DOCX" in raw or "docx" in raw or "zip" in raw:
        return "Failed to parse Word document: Corrupted XML or layout"
    if "Unicode" in raw or "encoding" in raw:
        return "Failed to parse document text: Unsupported or corrupt character encoding"

    return f"Ingestion error: {clean[:120]}"


class IngestionService:
    def __init__(
        self,
        document_repo: DocumentRepository,
        chunk_repo: DocumentChunkRepository,
        normalizer: Optional[BaseNormalizer] = None,
        structure_detector: Optional[BaseStructureDetector] = None,
        chunker: Optional[BaseChunker] = None,
        vector_store: Optional[VectorStoreService] = None,
        llm_gateway: Optional[LiteLLMGateway] = None,
        sparse_encoder: Optional[SparseEncoder] = None,
    ) -> None:
        self.document_repo = document_repo
        self.chunk_repo = chunk_repo
        self.normalizer = normalizer or TextNormalizer()
        self.structure_detector = structure_detector or StructureDetector()
        self.chunker = chunker or SemanticChunker()
        self.vector_store = vector_store
        self.llm_gateway = llm_gateway or get_litellm_gateway()
        self.sparse_encoder = sparse_encoder or SparseEncoder()

    async def ingest_document(
        self, document_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> bool:
        """
        Execute ingestion pipeline for document:
        1. Atomic claim for processing
        2. Loader -> Normalizer -> StructureDetector -> Chunker
        3. Persist chunks in PostgreSQL (document_chunks table)
        4. Generate dense embeddings & sparse lexical vectors
        5. Upsert points into Qdrant collection with workspace_id filter index
        6. Update document status to 'processed'
        """
        # 1. Atomic claim for processing
        claimed = await self.document_repo.claim_for_processing(document_id)
        if not claimed:
            logger.info(
                "Document %s already being processed or missing. Skipping.",
                document_id,
            )
            return False

        doc = await self.document_repo.get_by_id(document_id)
        if not doc or doc.workspace_id != workspace_id:
            await self.document_repo.update_status(
                document_id, "failed", error_message="Document or workspace invalid"
            )
            return False

        # 2. Out-of-transaction CPU parsing & chunking
        try:
            if not os.path.exists(doc.storage_key):
                raise FileNotFoundError(f"Storage file missing: {doc.storage_key}")

            loader_cls = LOADERS.get(doc.mime_type, TxtLoader)
            loader = loader_cls()

            extracted: ExtractedDocument = await loader.load(doc.storage_key, doc.mime_type)
            normalized = self.normalizer.normalize(extracted)
            nodes = self.structure_detector.detect_structure(normalized)
            processed_chunks: List[ProcessedChunk] = self.chunker.chunk(nodes)

            # 3. Transactional Success Path — Replace old chunks in PostgreSQL
            await self.chunk_repo.delete_by_document(document_id)
            saved_chunks = await self.chunk_repo.bulk_create(
                document_id, workspace_id, processed_chunks
            )

            # 4. Generate Dense & Sparse Vector Embeddings (if vector_store configured)
            if self.vector_store and saved_chunks:
                try:
                    chunk_texts = [c.content for c in saved_chunks]
                    dense_embeddings = await self.llm_gateway.generate_embeddings(chunk_texts)
                    sparse_vectors = self.sparse_encoder.encode_batch(chunk_texts)

                    await self.vector_store.upsert_chunks(
                        workspace_id=workspace_id,
                        document_id=document_id,
                        chunks=saved_chunks,
                        dense_embeddings=dense_embeddings,
                        sparse_vectors=sparse_vectors,
                    )
                except Exception as vec_exc:
                    logger.warning(
                        "Vector embedding/indexing encountered warning for doc %s: %s",
                        document_id,
                        vec_exc,
                    )

            await self.document_repo.update_status(
                document_id,
                status="processed",
                error_message=None,
                chunk_count=len(processed_chunks),
            )
            logger.info(
                "Ingestion succeeded for doc=%s chunks=%d",
                document_id,
                len(processed_chunks),
            )
            return True

        except Exception as exc:
            # 5. Failure Path — Log traceback server-side, write sanitized error to DB
            logger.exception("Ingestion pipeline failed for document %s", document_id)
            safe_err = sanitize_error_message(exc)
            await self.document_repo.update_status(
                document_id, status="failed", error_message=safe_err
            )
            return False
