"""
Unit tests for PlannerAgent across Quick, Deep, and Academic modes.
"""

from unittest.mock import AsyncMock
import pytest

from app.core.llm_gateway import GatewayResponse, LiteLLMGateway
from app.db.models.workspace import ResearchMode
from app.services.agents.planner import PlannerAgent


@pytest.mark.asyncio
async def test_planner_agent_generate_plan_success():
    mock_gateway = AsyncMock(spec=LiteLLMGateway)
    mock_gateway.complete.return_value = GatewayResponse(
        content="""{
            "title": "Quantum Error Correction Plan",
            "objectives": ["Analyze surface code fidelity"],
            "research_questions": ["What is the physical threshold?"],
            "hypotheses": ["Fidelity > 99% is achievable"],
            "search_strategy": {"keywords": ["surface code", "quantum error correction"]},
            "expected_sources": ["arXiv", "Nature"],
            "deliverables": ["Full Report"]
        }""",
        model="gpt-4o-mini",
        provider="openai",
    )

    planner = PlannerAgent(llm_gateway=mock_gateway)
    plan = await planner.generate_plan(
        title="Quantum Error Correction",
        description="Study scaling of qubits",
        research_mode=ResearchMode.ACADEMIC,
    )

    assert plan.title == "Quantum Error Correction Plan"
    assert len(plan.objectives) == 1
    assert len(plan.research_questions) == 1
    mock_gateway.complete.assert_called_once()


@pytest.mark.asyncio
async def test_planner_agent_fallback_on_invalid_json():
    mock_gateway = AsyncMock(spec=LiteLLMGateway)
    mock_gateway.complete.return_value = GatewayResponse(
        content="Not a valid json response from model",
        model="gpt-4o-mini",
        provider="openai",
    )

    planner = PlannerAgent(llm_gateway=mock_gateway)
    plan = await planner.generate_plan(
        title="AI Safety Alignment",
        research_mode=ResearchMode.QUICK,
    )

    # Deterministic fallback triggered
    assert plan.title == "Research Plan: AI Safety Alignment"
    assert len(plan.objectives) >= 1
    assert len(plan.research_questions) >= 1
