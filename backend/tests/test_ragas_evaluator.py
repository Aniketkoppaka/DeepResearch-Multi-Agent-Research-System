"""
Unit tests for RagasEvaluator and CostTracker.
"""

from unittest.mock import AsyncMock
import uuid
import pytest

from app.core.llm_gateway import GatewayResponse, LiteLLMGateway
from app.db.models.evidence import EvidenceNode
from app.services.agents.state import ResearchPlan
from app.services.evaluations.cost_tracker import CostTracker
from app.services.evaluations.ragas_evaluator import RagasEvaluator


def test_cost_tracker_calculation_and_breakdown():
    cost = CostTracker.calculate_cost(prompt_tokens=1000, completion_tokens=1000, model="gpt-4o-mini")
    assert cost > 0

    total_tokens, total_cost, breakdown = CostTracker.estimate_agent_breakdown(
        num_docs=3,
        num_claims=8,
        report_length=4000,
    )
    assert total_tokens > 0
    assert total_cost > 0
    assert "planner" in breakdown
    assert "synthesizer" in breakdown


@pytest.mark.asyncio
async def test_ragas_evaluator_scoring_success():
    mock_gateway = AsyncMock(spec=LiteLLMGateway)
    mock_gateway.complete.return_value = GatewayResponse(
        content="""{
            "faithfulness": 0.96,
            "answer_relevance": 0.94,
            "context_precision": 0.91,
            "verifiable_claims_count": 5,
            "unverifiable_claims_count": 0,
            "reasoning": "All key assertions correspond directly to cited evidence."
        }""",
        model="gpt-4o-mini",
        provider="openai",
    )

    evaluator = RagasEvaluator(llm_gateway=mock_gateway)
    plan = ResearchPlan(
        title="Agent Alignment Study",
        objectives=["Analyze alignment methods"],
        research_questions=["How to test alignment?"],
    )
    nodes = [
        EvidenceNode(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            source_id=uuid.uuid4(),
            claim_text="Alignment protocols decrease jailbreak vulnerability by 80%.",
            claim_type="FINDING",
            confidence_score=0.98,
            extracted_by_agent="fact_agent",
        )
    ]

    res = await evaluator.evaluate_report(
        plan=plan,
        report_markdown="# Alignment Report\n\nAlignment protocols decrease jailbreak vulnerability [1].",
        evidence_nodes=nodes,
    )

    assert res.faithfulness == 0.96
    assert res.answer_relevance == 0.94
    assert res.context_precision == 0.91
