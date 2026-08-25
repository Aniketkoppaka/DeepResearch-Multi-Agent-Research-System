"""
Deterministic text normalizer preserving structural boundaries
while cleaning Unicode and whitespace.
"""


import re
import unicodedata

from app.services.ingestion.base import BaseNormalizer, ExtractedDocument, ExtractedElement


class TextNormalizer(BaseNormalizer):
    def normalize(self, extracted: ExtractedDocument) -> ExtractedDocument:
        normalized_elements: list[ExtractedElement] = []

        for elem in extracted.elements:
            cleaned_text = self._clean_string(elem.text)
            if not cleaned_text:
                continue

            normalized_elements.append(
                ExtractedElement(
                    text=cleaned_text,
                    element_type=elem.element_type,
                    page_number=elem.page_number,
                    section_heading=self._clean_string(elem.section_heading)
                    if elem.section_heading
                    else None,
                    heading_level=elem.heading_level,
                    metadata=elem.metadata,
                )
            )

        cleaned_raw = self._clean_string(extracted.raw_text)

        return ExtractedDocument(
            raw_text=cleaned_raw,
            elements=normalized_elements,
            mime_type=extracted.mime_type,
            metadata=extracted.metadata,
        )

    def _clean_string(self, text: str) -> str:
        if not text:
            return ""

        # 1. Unicode NFC Normalization
        normalized = unicodedata.normalize("NFC", text)

        # 2. Replace non-breaking spaces with standard space
        normalized = normalized.replace("\u00a0", " ")

        # 3. Normalize line endings to \n
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

        # 4. Strip control characters (\x00-\x08, \x0b, \x0c, \x0e-\x1f, \x7f)
        normalized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", normalized)

        # 5. Collapse multiple horizontal spaces per line without destroying structural line breaks
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in normalized.split("\n")]

        # 6. Preserve structural paragraph breaks (\n\n)
        result = "\n".join(lines)
        result = re.sub(r"\n{3,}", "\n\n", result)
        return result.strip()
