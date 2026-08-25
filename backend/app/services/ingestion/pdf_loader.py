"""
PDF file loader using pypdf for page-by-page text extraction with page metadata.
"""

import os
from typing import List

from pypdf import PdfReader

from app.services.ingestion.base import (
    BaseLoader,
    ExtractedDocument,
    ExtractedElement,
    NodeType,
)


class PDFLoader(BaseLoader):
    async def load(self, file_path: str, mime_type: str) -> ExtractedDocument:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at path: {file_path}")

        elements: List[ExtractedElement] = []
        raw_text_parts: List[str] = []

        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)

            for page_idx, page in enumerate(reader.pages):
                page_num = page_idx + 1
                page_text = page.extract_text() or ""
                if not page_text.strip():
                    continue

                raw_text_parts.append(page_text)

                # Split page text into paragraphs while keeping page number association
                paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
                for para in paragraphs:
                    elements.append(
                        ExtractedElement(
                            text=para,
                            element_type=NodeType.PARAGRAPH,
                            page_number=page_num,
                            metadata={"total_pages": total_pages},
                        )
                    )

            full_text = "\n\n".join(raw_text_parts)
            return ExtractedDocument(
                raw_text=full_text,
                elements=elements,
                mime_type=mime_type,
                metadata={"total_pages": total_pages, "file_path": file_path},
            )
        except Exception as e:
            raise ValueError(f"Corrupted or invalid PDF file: {str(e)}") from e
