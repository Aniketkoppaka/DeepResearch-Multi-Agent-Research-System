"""
Plain text file loader supporting UTF-8 and encoding detection fallback.
"""

import os
from typing import List

from app.services.ingestion.base import (
    BaseLoader,
    ExtractedDocument,
    ExtractedElement,
    NodeType,
)


class TxtLoader(BaseLoader):
    async def load(self, file_path: str, mime_type: str) -> ExtractedDocument:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"TXT file not found at path: {file_path}")

        raw_bytes = open(file_path, "rb").read()
        if not raw_bytes:
            return ExtractedDocument(
                raw_text="",
                elements=[],
                mime_type=mime_type,
                metadata={"file_path": file_path},
            )

        # Attempt UTF-8 decode, fallback to latin-1
        text: str = ""
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                text = raw_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if not text and raw_bytes:
            text = raw_bytes.decode("latin-1", errors="replace")

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        elements: List[ExtractedElement] = []
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        for para in paragraphs:
            elements.append(
                ExtractedElement(
                    text=para,
                    element_type=NodeType.PARAGRAPH,
                )
            )

        return ExtractedDocument(
            raw_text=text,
            elements=elements,
            mime_type=mime_type,
            metadata={"file_path": file_path},
        )
