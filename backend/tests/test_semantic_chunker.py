"""
Unit tests for text normalizer and semantic chunker.
"""

from app.services.ingestion.base import DocumentNode, ExtractedDocument, ExtractedElement, NodeType
from app.services.ingestion.normalizer import TextNormalizer
from app.services.ingestion.semantic_chunker import SemanticChunker


def test_text_normalizer():
    normalizer = TextNormalizer()
    raw = ExtractedDocument(
        raw_text="Header\u00a0Text\r\n\r\nParagraph\x00 with control chars.\n\n\n\nExtra lines.",
        elements=[
            ExtractedElement(
                text="Header\u00a0Text\r\n\r\nParagraph\x00 with control chars.",
                element_type=NodeType.PARAGRAPH,
            )
        ],
        mime_type="text/plain",
    )

    normalized = normalizer.normalize(raw)
    assert "\u00a0" not in normalized.raw_text
    assert "\x00" not in normalized.raw_text
    assert "Header Text" in normalized.elements[0].text


def test_semantic_chunker_heading_boundaries():
    chunker = SemanticChunker(target_size=200, max_size=300, overlap=50)

    nodes = [
        DocumentNode(content="Section 1 Header", node_type=NodeType.HEADING, heading_level=1, section_heading="Section 1 Header"),
        DocumentNode(content="Short paragraph in section 1.", node_type=NodeType.PARAGRAPH, section_heading="Section 1 Header"),
        DocumentNode(content="Section 2 Header", node_type=NodeType.HEADING, heading_level=1, section_heading="Section 2 Header"),
        DocumentNode(content="Short paragraph in section 2.", node_type=NodeType.PARAGRAPH, section_heading="Section 2 Header"),
    ]

    chunks = chunker.chunk(nodes)
    assert len(chunks) == 2
    assert chunks[0].section_heading == "Section 1 Header"
    assert chunks[1].section_heading == "Section 2 Header"
    assert chunks[0].estimated_tokens > 0


def test_semantic_chunker_sliding_window_fallback():
    chunker = SemanticChunker(target_size=100, max_size=150, overlap=20)

    # Raw single node without sentence boundaries or headings exceeding max_size
    nodes = [
        DocumentNode(content="A" * 350, node_type=NodeType.PARAGRAPH)
    ]

    chunks = chunker.chunk(nodes)
    assert len(chunks) >= 3
    assert chunks[0].metadata_json["strategy"] in ("sentence_boundary", "sliding_window_fallback")
