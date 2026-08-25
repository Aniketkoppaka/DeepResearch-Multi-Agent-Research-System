"""
Report Synthesizer Agent.
Generates comprehensive, multi-section research reports with inline [X] citations from EKG evidence.
"""

import logging
from typing import Any, Dict, List, Optional

from app.core.llm_gateway import LiteLLMGateway, get_litellm_gateway
from app.db.models.evidence import EvidenceEdge, EvidenceNode, EvidenceSource
from app.db.models.workspace import ResearchMode
from app.services.agents.state import ResearchPlan

logger = logging.getLogger(__name__)


class SynthesizerAgent:
    def __init__(self, llm_gateway: Optional[LiteLLMGateway] = None) -> None:
        self.llm_gateway = llm_gateway or get_litellm_gateway()

    async def synthesize_report(
        self,
        plan: ResearchPlan,
        sources: List[EvidenceSource],
        nodes: List[EvidenceNode],
        contradictions: List[EvidenceEdge],
        research_mode: ResearchMode = ResearchMode.DEEP,
        additional_guidelines: Optional[str] = None,
    ) -> tuple[str, Dict[str, Any]]:
        """
        Synthesizes research report with numbered citations [1], [2] and builds citation map.
        """
        # 1. Build Citation Index Map
        citation_map: Dict[str, Any] = {}
        evidence_context_lines: List[str] = []

        for idx, node in enumerate(nodes[:25], start=1):
            tag = f"[{idx}]"
            source_match = next((s for s in sources if s.id == node.source_id), None)
            source_title = source_match.title if source_match else "Verified Evidence"
            source_url = source_match.url if source_match else None
            cred_score = source_match.credibility_score if source_match else 0.5

            citation_map[tag] = {
                "tag": tag,
                "node_id": str(node.id),
                "source_id": str(node.source_id),
                "source_title": source_title,
                "source_url": source_url,
                "credibility_score": cred_score,
                "quote_snippet": node.claim_text,
                "claim_type": node.claim_type,
            }

            evidence_context_lines.append(
                f"{tag} ({node.claim_type}) [Credibility: {cred_score:.2f}]: {node.claim_text}"
            )

        contradiction_context: List[str] = []
        for c in contradictions:
            contradiction_context.append(
                f"Contradiction: '{c.source_node.claim_text if c.source_node else 'Node A'}' "
                f"CONTRADICTS '{c.target_node.claim_text if c.target_node else 'Node B'}' "
                f"(Reason: {c.reasoning or 'Opposing claims'})"
            )

        system_prompt = (
            "You are a Principal Research Synthesizer writing a publication-grade research report. "
            "You MUST integrate numbered citations [1], [2] directly inline after assertions. "
            "Structure the report with markdown headings: \n"


            "# Title\n"
            "## Executive Summary\n"
            "## Key Findings & Empirical Analysis\n"
            "## Contradictions & Disputed Points (if applicable)\n"
            "## Strategic Implications & Recommendations\n"
            "## References (list citation numbers and titles)"
        )

        user_content = (
            f"Research Title: {plan.title}\n"
            f"Mode: {research_mode.value}\n"
            f"Objectives: {plan.objectives}\n"
            f"Research Questions: {plan.research_questions}\n\n"
            f"AVAILABLE NUMBERED EVIDENCE CITATIONS:\n"
            + "\n".join(evidence_context_lines)
            + "\n\n"
        )
        if contradiction_context:
            user_content += (
                "DISCOVERED CONTRADICTIONS IN EVIDENCE GRAPH:\n"
                + "\n".join(contradiction_context)
                + "\n\n"
            )
        if additional_guidelines:
            user_content += f"Additional Guidelines: {additional_guidelines}\n"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        try:
            res = await self.llm_gateway.complete(messages=messages)
            markdown_content = res.content.strip()
            return markdown_content, citation_map
        except Exception as exc:
            logger.warning("Synthesis error, using fallback template: %s", exc)
            fallback_md = (
                f"# Research Report: {plan.title}\n\n"
                f"## Executive Summary\n"
                f"This report synthesizes key findings on {plan.title}.\n\n"
                f"## Key Findings\n"
            )
            for tag, meta in list(citation_map.items())[:5]:
                fallback_md += f"- {meta['quote_snippet']} {tag}\n"

            fallback_md += "\n## References\n"
            for tag, meta in list(citation_map.items())[:5]:
                fallback_md += f"{tag} {meta['source_title']}\n"

            return fallback_md, citation_map
