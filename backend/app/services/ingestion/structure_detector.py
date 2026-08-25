"""
Structure detector converting normalized elements into a sequence of DocumentNode objects.
"""

from typing import List, Optional

from app.services.ingestion.base import (
    BaseStructureDetector,
    DocumentNode,
    ExtractedDocument,
    NodeType,
)


class StructureDetector(BaseStructureDetector):
    def detect_structure(self, extracted: ExtractedDocument) -> List[DocumentNode]:
        nodes: List[DocumentNode] = []
        current_heading: Optional[str] = None
        current_level: Optional[int] = None

        for elem in extracted.elements:
            if elem.element_type == NodeType.HEADING:
                current_heading = elem.text
                current_level = elem.heading_level
                nodes.append(
                    DocumentNode(
                        content=elem.text,
                        node_type=NodeType.HEADING,
                        heading_level=elem.heading_level,
                        section_heading=current_heading,
                        page_number=elem.page_number,
                        metadata=elem.metadata,
                    )
                )
            else:
                heading_ctx = elem.section_heading or current_heading
                nodes.append(
                    DocumentNode(
                        content=elem.text,
                        node_type=elem.element_type,
                        heading_level=current_level,
                        section_heading=heading_ctx,
                        page_number=elem.page_number,
                        metadata=elem.metadata,
                    )
                )

        return nodes
