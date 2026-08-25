"""
Unit tests for ReportSynthesizerAgent.
"""

from unittest.mock import AsyncMock
import uuid
import pytest

from app.core.llm_gateway import GatewayResponse, LiteLLMGateway
from app.db.models.evidence import EvidenceNode, EvidenceSource
from app.db.models.workspace import ResearchMode
from app.services.agents.state import ResearchPlan
from app.services.agents.synthesizer import SynthesizerAgent


@pytest.mark.asyncio
async def test_synthesizer_agent_generates_report_with_citations():
    mock_gateway = AsyncMock(spec=LiteLLMGateway)
    mock_gateway.complete.return_value = GatewayResponse(
        content="""# Autonomous Multi-Agent Synthesis
## Executive Summary
Recent breakthroughs demonstrate that multi-agent teams outperform single prompts [1].

## Key Findings
Transformer inference scaling limits are mitigated by kernel fusion [2].

## References
[1] Multi-Agent Systems Paper
[2] FlashAttention Deep Dive
""",
        model="gpt-4o-mini",
        provider="openai",
    )

    synthesizer = SynthesizerAgent(llm_gateway=mock_gateway)

    plan = ResearchPlan(
        title="Multi-Agent LLM Architectures",
        objectives=["Analyze scaling and coordination"],
        research_questions=["How to optimize agent loops?"],
    )

    src1_id = uuid.uuid4()
    src2_id = uuid.uuid4()
    sources = [
        EvidenceSource(id=src1_id, workspace_id=uuid.uuid4(), title="Multi-Agent Systems Paper", credibility_score=0.95),
        EvidenceSource(id=src2_id, workspace_id=uuid.uuid4(), title="FlashAttention Deep Dive", credibility_score=0.90),
    ]

    nodes = [
        EvidenceNode(id=uuid.uuid4(), workspace_id=uuid.uuid4(), source_id=src1_id, claim_text="Multi-agent teams outperform single prompts.", claim_type="FINDING", confidence_score=0.98, extracted_by_agent="fact_agent"),
        EvidenceNode(id=uuid.uuid4(), workspace_id=uuid.uuid4(), source_id=src2_id, claim_text="Transformer inference scaling limits are mitigated by kernel fusion.", claim_type="FACT", confidence_score=0.95, extracted_by_agent="fact_agent"),
    ]

    markdown, citation_map = await synthesizer.synthesize_report(
        plan=plan,
        sources=sources,
        nodes=nodes,
        contradictions=[],
        research_mode=ResearchMode.DEEP,
    )

    assert "# Autonomous Multi-Agent Synthesis" in markdown
    assert "[1]" in citation_map
    assert "[2]" in citation_map
    assert citation_map["[1]"]["source_title"] == "Multi-Agent Systems Paper"
