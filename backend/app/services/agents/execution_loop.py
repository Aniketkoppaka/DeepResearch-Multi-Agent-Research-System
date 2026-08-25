"""
Research Execution Loop & Convergence Engine.
Coordinates multi-iteration search, fact extraction, and relational EKG linking.
"""

import logging
from typing import Any, Dict, List, Optional
import uuid

from fastapi import HTTPException, status

from app.db.models.evidence import EvidenceNode, EvidenceSource
from app.db.models.workspace import PlanStatus, ResearchMode
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.agents.fact_extractor import FactExtractorAgent
from app.services.agents.search_agent import SearchAgent, SearchExecutionResult
from app.services.agents.state import ResearchPlan
from app.services.evidence.credibility import calculate_credibility_score

logger = logging.getLogger(__name__)

MAX_ITERATIONS_BY_MODE = {
    ResearchMode.QUICK: 2,
    ResearchMode.DEEP: 4,
    ResearchMode.ACADEMIC: 5,
}


class ResearchExecutionLoop:
    def __init__(
        self,
        workspace_repo: WorkspaceRepository,
        evidence_repo: EvidenceRepository,
        search_agent: SearchAgent,
        fact_extractor: Optional[FactExtractorAgent] = None,
    ) -> None:
        self.workspace_repo = workspace_repo
        self.evidence_repo = evidence_repo
        self.search_agent = search_agent
        self.fact_extractor = fact_extractor or FactExtractorAgent()

    async def execute_iteration(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """
        Executes a single recursive iteration step:
        1. Formulate & Execute Search Queries (RAG + Web)
        2. Extract atomic claims & entities
        3. Persist sources, nodes, and relational edges
        4. Update workspace execution state & check convergence
        """
        ws = await self.workspace_repo.get_by_id_and_user(workspace_id, user_id)
        if not ws:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

        if ws.plan_status != PlanStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Research plan must be approved before execution",
            )

        plan = ResearchPlan.model_validate(ws.research_plan or {})
        max_iters = MAX_ITERATIONS_BY_MODE.get(ws.research_mode, 3)

        state = ws.execution_state or {}
        current_iter = state.get("current_iteration", 0) + 1

        # 1. Search Query Formulation & Execution
        queries = await self.search_agent.formulate_queries(plan, iteration=current_iter)
        search_res: SearchExecutionResult = await self.search_agent.execute_search(
            workspace_id=workspace_id,
            queries=queries,
        )

        extracted_nodes: List[EvidenceNode] = []

        # 2. Process Web Results -> EvidenceSources & Claims
        for web_item in search_res.web_results:
            cred_score, cred_breakdown = calculate_credibility_score(
                url=web_item.url,
                domain=web_item.domain,
            )
            source = EvidenceSource(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                url=web_item.url,
                title=web_item.title,
                domain=web_item.domain,
                credibility_score=cred_score,
                credibility_breakdown=cred_breakdown,
            )
            saved_source = await self.evidence_repo.create_source(source)

            # Extract facts from snippet
            claims = await self.fact_extractor.extract_claims_from_text(
                source_title=web_item.title,
                text_content=web_item.content,
                research_context=plan.title,
            )
            for claim in claims:
                node = EvidenceNode(
                    id=uuid.uuid4(),
                    workspace_id=workspace_id,
                    source_id=saved_source.id,
                    claim_text=claim.claim_text,
                    claim_type=claim.claim_type,
                    confidence_score=claim.confidence_score,
                    extracted_by_agent="fact_extractor_web",
                    supporting_reasoning=claim.supporting_reasoning,
                    entities=claim.entities,
                )
                saved_node = await self.evidence_repo.create_node(node)
                extracted_nodes.append(saved_node)

        # 3. Process Document RAG Chunks -> Claims
        for chunk in search_res.document_chunks:
            claims = await self.fact_extractor.extract_claims_from_text(
                source_title=f"Doc chunk #{chunk.chunk_index}",
                text_content=chunk.content,
                research_context=plan.title,
            )
            if claims:
                # Reuse or create document source reference
                doc_source = EvidenceSource(
                    id=uuid.uuid4(),
                    workspace_id=workspace_id,
                    title=f"Workspace Document ({chunk.document_id})",
                    credibility_score=0.95,
                    credibility_breakdown={"type": "verified_uploaded_document"},
                )
                saved_doc_source = await self.evidence_repo.create_source(doc_source)

                for claim in claims:
                    node = EvidenceNode(
                        id=uuid.uuid4(),
                        workspace_id=workspace_id,
                        source_id=saved_doc_source.id,
                        claim_text=claim.claim_text,
                        claim_type=claim.claim_type,
                        confidence_score=claim.confidence_score,
                        extracted_by_agent="fact_extractor_rag",
                        supporting_reasoning=claim.supporting_reasoning,
                        entities=claim.entities,
                    )
                    saved_node = await self.evidence_repo.create_node(node)
                    extracted_nodes.append(saved_node)

        # 4. Check Convergence & Relational Edge Linking
        is_converged = current_iter >= max_iters or len(extracted_nodes) >= 15
        progress = min(100, int((current_iter / max_iters) * 80) + 20)

        new_status = "ready_for_synthesis" if is_converged else "executing"
        ws.execution_state = {
            "status": new_status,
            "current_iteration": current_iter,
            "max_iterations": max_iters,
            "progress_percentage": progress,
            "claims_extracted_count": len(extracted_nodes),
            "status_messages": [
                f"Completed research iteration {current_iter}/{max_iters}. "
                f"Extracted {len(extracted_nodes)} factual claims."
            ],
        }
        await self.workspace_repo.update(ws)

        return {
            "workspace_id": workspace_id,
            "iteration": current_iter,
            "max_iterations": max_iters,
            "is_converged": is_converged,
            "claims_extracted": len(extracted_nodes),
            "status": new_status,
        }
