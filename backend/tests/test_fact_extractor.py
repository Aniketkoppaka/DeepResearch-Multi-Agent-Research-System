"""
Unit tests for FactExtractorAgent structured claim extraction.
"""

from unittest.mock import AsyncMock
import pytest

from app.core.llm_gateway import GatewayResponse, LiteLLMGateway
from app.services.agents.fact_extractor import FactExtractorAgent


@pytest.mark.asyncio
async def test_fact_extractor_structured_claims_success():
    mock_gateway = AsyncMock(spec=LiteLLMGateway)
    mock_gateway.complete.return_value = GatewayResponse(
        content="""[
            {
                "claim_text": "Transformer attention mechanism scales quadratically with sequence length O(N^2).",
                "claim_type": "FACT",
                "confidence_score": 0.99,
                "entities": ["Transformers", "Self-Attention", "Complexity"],
                "supporting_reasoning": "Standard computational complexity proof of self-attention."
            },
            {
                "claim_text": "FlashAttention reduces memory access overhead by fusing attention kernels.",
                "claim_type": "FINDING",
                "confidence_score": 0.95,
                "entities": ["FlashAttention", "GPU IO"],
                "supporting_reasoning": "Empirical IO-aware kernel tiling benchmarks."
            }
        ]""",
        model="gpt-4o-mini",
        provider="openai",
    )

    extractor = FactExtractorAgent(llm_gateway=mock_gateway)
    claims = await extractor.extract_claims_from_text(
        source_title="Attention Is All You Need",
        text_content="FlashAttention and Transformer self-attention complexity analysis...",
        research_context="Efficient Transformer Architectures",
    )

    assert len(claims) == 2
    assert claims[0].claim_type == "FACT"
    assert claims[1].claim_type == "FINDING"
    assert "FlashAttention" in claims[1].entities
    mock_gateway.complete.assert_called_once()


@pytest.mark.asyncio
async def test_fact_extractor_empty_content():
    extractor = FactExtractorAgent()
    claims = await extractor.extract_claims_from_text(
        source_title="Empty Doc",
        text_content="",
    )
    assert claims == []
