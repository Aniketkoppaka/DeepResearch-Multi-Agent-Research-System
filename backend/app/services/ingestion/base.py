"""
Core interfaces, data classes, and protocols for the document ingestion pipeline.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class NodeType(str, Enum):
    TITLE = "TITLE"
    HEADING = "HEADING"
    PARAGRAPH = "PARAGRAPH"
    LIST_ITEM = "LIST_ITEM"
    CODE_BLOCK = "CODE_BLOCK"
    TABLE = "TABLE"
    PAGE_BREAK = "PAGE_BREAK"


@dataclass
class ExtractedElement:
    """Individual extracted text block from a file loader."""

    text: str
    element_type: NodeType = NodeType.PARAGRAPH
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    heading_level: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedDocument:
    """Standardized representation returned by all file loaders."""

    raw_text: str
    elements: List[ExtractedElement]
    mime_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentNode:
    """Structural node created during structure detection."""

    content: str
    node_type: NodeType
    heading_level: Optional[int] = None
    section_heading: Optional[str] = None
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessedChunk:
    """Data object representing a single generated semantic chunk."""

    content: str
    chunk_index: int
    estimated_tokens: int
    section_heading: Optional[str] = None
    page_number: Optional[int] = None
    metadata_json: Dict[str, Any] = field(default_factory=dict)


class BaseLoader(ABC):
    """Abstract protocol for file format loaders."""

    @abstractmethod
    async def load(self, file_path: str, mime_type: str) -> ExtractedDocument:
        """Parse raw file bytes and extract structured text elements."""
        pass


class BaseNormalizer(ABC):
    """Abstract protocol for text normalization."""

    @abstractmethod
    def normalize(self, extracted: ExtractedDocument) -> ExtractedDocument:
        """Clean and normalize extracted document text."""
        pass


class BaseStructureDetector(ABC):
    """Abstract protocol for structure detection."""

    @abstractmethod
    def detect_structure(self, extracted: ExtractedDocument) -> List[DocumentNode]:
        """Build a sequence of structural nodes from normalized elements."""
        pass


class BaseChunker(ABC):
    """Abstract protocol for semantic chunking."""

    @abstractmethod
    def chunk(self, nodes: List[DocumentNode]) -> List[ProcessedChunk]:
        """Partition structural nodes into semantic chunks."""
        pass
