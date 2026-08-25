"""
Semantic chunker implementing heading-aware, sentence-aware splitting with sliding-window fallback.
"""

import math
import re
from typing import List, Optional

from app.core.config import settings
from app.services.ingestion.base import (
    BaseChunker,
    DocumentNode,
    NodeType,
    ProcessedChunk,
)


class SemanticChunker(BaseChunker):
    def __init__(
        self,
        target_size: Optional[int] = None,
        max_size: Optional[int] = None,
        overlap: Optional[int] = None,
    ) -> None:
        self.target_size = target_size or settings.CHUNK_TARGET_SIZE
        self.max_size = max_size or settings.CHUNK_MAX_SIZE
        self.overlap = overlap or settings.CHUNK_OVERLAP

    def chunk(self, nodes: List[DocumentNode]) -> List[ProcessedChunk]:
        chunks: List[ProcessedChunk] = []
        chunk_index = 0

        if not nodes:
            return chunks

        # Group nodes by section heading where possible
        sections: List[List[DocumentNode]] = []
        current_section: List[DocumentNode] = []

        for node in nodes:
            if node.node_type == NodeType.HEADING and current_section:
                sections.append(current_section)
                current_section = [node]
            else:
                current_section.append(node)
        if current_section:
            sections.append(current_section)

        for section_nodes in sections:
            section_text = "\n\n".join([n.content for n in section_nodes])
            heading = section_nodes[0].section_heading
            page_num = section_nodes[0].page_number

            # 1. Section fits within max size
            if len(section_text) <= self.max_size:
                if section_text.strip():
                    tokens = math.ceil(len(section_text) / 4)
                    chunks.append(
                        ProcessedChunk(
                            content=section_text,
                            chunk_index=chunk_index,
                            estimated_tokens=tokens,
                            section_heading=heading,
                            page_number=page_num,
                            metadata_json={
                                "char_count": len(section_text),
                                "strategy": "heading_boundary",
                            },
                        )
                    )
                    chunk_index += 1
                continue

            # 2. Section is oversized — split into paragraph blocks
            paragraphs = [n.content for n in section_nodes if n.content.strip()]
            buffer: List[str] = []
            buffer_len = 0

            for para in paragraphs:
                # Individual paragraph exceeds max_size → split by sentence or sliding window
                if len(para) > self.max_size:
                    if buffer:
                        text = "\n\n".join(buffer)
                        chunks.append(
                            ProcessedChunk(
                                content=text,
                                chunk_index=chunk_index,
                                estimated_tokens=math.ceil(len(text) / 4),
                                section_heading=heading,
                                page_number=page_num,
                                metadata_json={
                                    "char_count": len(text),
                                    "strategy": "paragraph_boundary",
                                },
                            )
                        )
                        chunk_index += 1
                        buffer = []
                        buffer_len = 0

                    sub_chunks = self._split_large_text(para, heading, page_num, chunk_index)
                    chunks.extend(sub_chunks)
                    chunk_index += len(sub_chunks)
                    continue

                if buffer_len + len(para) + 2 <= self.target_size:
                    buffer.append(para)
                    buffer_len += len(para) + 2
                else:
                    if buffer:
                        text = "\n\n".join(buffer)
                        chunks.append(
                            ProcessedChunk(
                                content=text,
                                chunk_index=chunk_index,
                                estimated_tokens=math.ceil(len(text) / 4),
                                section_heading=heading,
                                page_number=page_num,
                                metadata_json={
                                    "char_count": len(text),
                                    "strategy": "paragraph_boundary",
                                },
                            )
                        )
                        chunk_index += 1
                    buffer = [para]
                    buffer_len = len(para)

            if buffer:
                text = "\n\n".join(buffer)
                chunks.append(
                    ProcessedChunk(
                        content=text,
                        chunk_index=chunk_index,
                        estimated_tokens=math.ceil(len(text) / 4),
                        section_heading=heading,
                        page_number=page_num,
                        metadata_json={
                            "char_count": len(text),
                            "strategy": "paragraph_boundary",
                        },
                    )
                )
                chunk_index += 1

        return chunks

    def _split_large_text(
        self,
        text: str,
        heading: Optional[str],
        page_num: Optional[int],
        start_index: int,
    ) -> List[ProcessedChunk]:
        """Split a large paragraph using sentence boundaries or sliding window fallback."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        result: List[ProcessedChunk] = []
        idx = start_index

        if len(sentences) > 1:
            buf: List[str] = []
            buf_len = 0
            for sent in sentences:
                if buf_len + len(sent) + 1 <= self.target_size:
                    buf.append(sent)
                    buf_len += len(sent) + 1
                else:
                    if buf:
                        stext = " ".join(buf)
                        result.append(
                            ProcessedChunk(
                                content=stext,
                                chunk_index=idx,
                                estimated_tokens=math.ceil(len(stext) / 4),
                                section_heading=heading,
                                page_number=page_num,
                                metadata_json={
                                    "char_count": len(stext),
                                    "strategy": "sentence_boundary",
                                },
                            )
                        )
                        idx += 1
                    buf = [sent]
                    buf_len = len(sent)
            if buf:
                stext = " ".join(buf)
                result.append(
                    ProcessedChunk(
                        content=stext,
                        chunk_index=idx,
                        estimated_tokens=math.ceil(len(stext) / 4),
                        section_heading=heading,
                        page_number=page_num,
                        metadata_json={
                            "char_count": len(stext),
                            "strategy": "sentence_boundary",
                        },
                    )
                )
                idx += 1
            return result

        # Sliding window fallback for raw continuous text without sentence boundaries
        step = self.target_size - self.overlap
        if step <= 0:
            step = self.target_size // 2

        for i in range(0, len(text), step):
            slice_text = text[i : i + self.target_size]
            if slice_text.strip():
                result.append(
                    ProcessedChunk(
                        content=slice_text,
                        chunk_index=idx,
                        estimated_tokens=math.ceil(len(slice_text) / 4),
                        section_heading=heading,
                        page_number=page_num,
                        metadata_json={
                            "char_count": len(slice_text),
                            "strategy": "sliding_window_fallback",
                        },
                    )
                )
                idx += 1

        return result
