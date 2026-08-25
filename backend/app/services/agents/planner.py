"""
Research Planner Agent.
Generates structured mode-aware (Quick, Deep, Academic) research plans using LiteLLM.
"""

import json
import logging
from typing import Any, Dict, Optional

from app.core.llm_gateway import LiteLLMGateway, get_litellm_gateway
from app.db.models.workspace import ResearchMode
from app.services.agents.state import ResearchPlan

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPTS = {
    ResearchMode.QUICK: (
        "You are an expert Research Planner operating in QUICK mode. "
        "Create a streamlined, targeted research plan consisting of 1-2 core objectives, "
        "2-3 specific research questions, key search keywords, and a concise deliverable outline."
    ),
    ResearchMode.DEEP: (
        "You are an expert Research Planner operating in DEEP mode. "
        "Create an exhaustive, multi-faceted research plan covering 3-5 core objectives, "
        "4-6 detailed research questions, initial hypotheses, multi-source search strategies, "
        "and comprehensive report deliverables."
    ),
    ResearchMode.ACADEMIC: (
        "You are an expert Academic Research Planner operating in ACADEMIC mode. "
        "Create a rigorous scientific literature review plan covering theoretical foundations, "
        "empirical methodologies, comparative hypotheses, peer-reviewed database targets, "
        "and formal academic paper deliverables with citations."
    ),

}


class PlannerAgent:
    def __init__(self, llm_gateway: Optional[LiteLLMGateway] = None) -> None:
        self.llm_gateway = llm_gateway or get_litellm_gateway()

    async def generate_plan(
        self,
        title: str,
        description: Optional[str] = None,
        research_mode: ResearchMode = ResearchMode.DEEP,
        user_feedback: Optional[str] = None,
    ) -> ResearchPlan:
        system_prompt = PLANNER_SYSTEM_PROMPTS.get(
            research_mode, PLANNER_SYSTEM_PROMPTS[ResearchMode.DEEP]
        )

        user_content = f"Research Topic: {title}\n"
        if description:
            user_content += f"Detailed Brief: {description}\n"
        if user_feedback:
            user_content += f"\nUser Feedback / Refinement Instructions: {user_feedback}\n"

        user_content += (
            "\nOutput ONLY a valid JSON object strictly matching this schema:\n"
            "{\n"
            '  "title": "string",\n'
            '  "objectives": ["string"],\n'
            '  "research_questions": ["string"],\n'
            '  "hypotheses": ["string"],\n'
            '  "search_strategy": {\n'
            '    "keywords": ["string"],\n'
            '    "domains": ["string"],\n'
            '    "max_depth": 3\n'
            '  },\n'
            '  "expected_sources": ["string"],\n'
            '  "deliverables": ["string"]\n'
            "}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        try:
            response = await self.llm_gateway.complete(messages=messages)
            content = response.content.strip()

            # Clean markdown codeblocks if wrapped
            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            parsed: Dict[str, Any] = json.loads(content)
            return ResearchPlan.model_validate(parsed)
        except Exception as exc:
            logger.warning("Structured plan generation failed or fallback triggered: %s", exc)
            # Safe deterministic fallback plan
            return ResearchPlan(
                title=f"Research Plan: {title}",
                objectives=[f"Investigate core dimensions of {title}"],
                research_questions=[
                    f"What are the primary factors affecting {title}?",
                    f"What empirical evidence supports current findings in {title}?",
                ],
                hypotheses=[
                    f"Comprehensive analysis will uncover key actionable findings for {title}."
                ],
                search_strategy={"keywords": [title], "max_depth": 2},
                expected_sources=["Academic journals", "Industry reports", "Web articles"],
                deliverables=["Executive Summary", "Key Findings & Evidence", "Conclusion"],
            )

