"""
Fact Extractor Agent.
Extracts structured atomic claims, entities, and confidence scores from retrieved passages.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.llm_gateway import LiteLLMGateway, get_litellm_gateway

logger = logging.getLogger(__name__)


class ExtractedClaim(BaseModel):
    claim_text: str = Field(..., min_length=1, description="Atomic factual or analytical claim")
    claim_type: str = Field(
        default="FACT",
        description="Claim classification: FACT, STATISTIC, FINDING, HYPOTHESIS, or OPINION",
    )
    confidence_score: float = Field(
        default=0.9, ge=0.0, le=1.0, description="Confidence in accuracy of extraction"
    )
    entities: List[str] = Field(
        default_factory=list, description="Key named entities, concepts, or technologies"
    )
    supporting_reasoning: Optional[str] = Field(
        default=None, description="Contextual reasoning supporting why this claim is valid"
    )


class FactExtractorAgent:
    def __init__(self, llm_gateway: Optional[LiteLLMGateway] = None) -> None:
        self.llm_gateway = llm_gateway or get_litellm_gateway()

    async def extract_claims_from_text(
        self,
        source_title: str,
        text_content: str,
        research_context: Optional[str] = None,
    ) -> List[ExtractedClaim]:
        if not text_content.strip():
            return []

        system_prompt = (
            "You are an expert Fact Extraction Agent in a Multi-Agent Deep Research System. "
            "Your task is to analyze source material and extract 1-5 atomic claims. "
            "Classify each claim strictly as: FACT, STATISTIC, FINDING, HYPOTHESIS, or OPINION. "
            "Assign a confidence score (0.0 to 1.0) and identify key named entities or concepts."
        )


        user_content = f"Source Document/Page: {source_title}\n"
        if research_context:
            user_content += f"Research Context/Objective: {research_context}\n"
        user_content += f"\nContent Passage:\n{text_content[:3000]}\n"
        user_content += (
            "\nOutput ONLY a valid JSON array of objects strictly matching this schema:\n"
            "[\n"
            "  {\n"
            '    "claim_text": "string",\n'
            '    "claim_type": "FACT" | "STATISTIC" | "FINDING" | "HYPOTHESIS" | "OPINION",\n'
            '    "confidence_score": 0.95,\n'
            '    "entities": ["entity1", "entity2"],\n'
            '    "supporting_reasoning": "string"\n'
            "  }\n"
            "]"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        try:
            response = await self.llm_gateway.complete(messages=messages)
            content = response.content.strip()

            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            parsed: List[Dict[str, Any]] = json.loads(content)
            if not isinstance(parsed, list):
                return []

            claims: List[ExtractedClaim] = []
            for item in parsed:
                try:
                    claims.append(ExtractedClaim.model_validate(item))
                except Exception as val_err:
                    logger.warning("Claim validation failed: %s", val_err)
            return claims
        except Exception as exc:
            logger.warning("Fact extraction failed or triggered fallback: %s", exc)
            # Safe heuristic fallback: create 1 finding from the first sentence
            first_sentence = text_content.split(".")[0].strip()
            if len(first_sentence) > 15:
                return [
                    ExtractedClaim(
                        claim_text=first_sentence,
                        claim_type="FINDING",
                        confidence_score=0.75,
                        entities=[source_title],
                        supporting_reasoning=f"Extracted from {source_title}",
                    )
                ]
            return []
