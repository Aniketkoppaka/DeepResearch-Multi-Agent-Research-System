"""
Markdown file loader parsing heading hierarchy (#, ##, ###) and list structures.
"""

import os
import re
from typing import List

from app.services.ingestion.base import (
    BaseLoader,
    ExtractedDocument,
    ExtractedElement,
    NodeType,
)


class MarkdownLoader(BaseLoader):
    async def load(self, file_path: str, mime_type: str) -> ExtractedDocument:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Markdown file not found at path: {file_path}")

        raw_bytes = open(file_path, "rb").read()
        text = raw_bytes.decode("utf-8", errors="replace")

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        elements: List[ExtractedElement] = []
        current_heading: str = ""

        # Process text line by line / block by block
        blocks = [b.strip() for b in text.split("\n\n") if b.strip()]


        for block in blocks:
            # Check for Markdown heading (# Heading)
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", block)
            if heading_match:
                hashes, title = heading_match.groups()
                level = len(hashes)
                current_heading = title.strip()
                elements.append(
                    ExtractedElement(
                        text=current_heading,
                        element_type=NodeType.HEADING,
                        heading_level=level,
                        section_heading=current_heading,
                    )
                )
                continue

            # Check for list items (- item, * item, 1. item)
            if re.match(r"^([\*\-\+]|\d+\.)\s+", block):
                elements.append(
                    ExtractedElement(
                        text=block,
                        element_type=NodeType.LIST_ITEM,
                        section_heading=current_heading if current_heading else None,
                    )
                )
                continue

            # Default paragraph
            elements.append(
                ExtractedElement(
                    text=block,
                    element_type=NodeType.PARAGRAPH,
                    section_heading=current_heading if current_heading else None,
                )
            )

        return ExtractedDocument(
            raw_text=text,
            elements=elements,
            mime_type=mime_type,
            metadata={"file_path": file_path},
        )
