"""
Integration tests for Evidence Knowledge Graph (EKG) models, repository, and API endpoints.
"""

from datetime import datetime, timezone
import uuid
import pytest
from httpx import AsyncClient

from app.db.models.evidence import EvidenceEdge, EvidenceNode, EvidenceSource
from app.db.models.workspace import Workspace
from app.repositories.evidence_repository import EvidenceRepository


@pytest.mark.asyncio
async def test_evidence_repository_crud(db_session):
    repo = EvidenceRepository(db_session)
    user_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    # Create workspace directly
    ws = Workspace(
        id=ws_id,
        user_id=user_id,
        title="Evidence Research WS",
    )
    db_session.add(ws)
    await db_session.commit()

    # 1. Create EvidenceSource
    source = EvidenceSource(
        id=uuid.uuid4(),
        workspace_id=ws_id,
        url="https://nature.com/articles/s41586-024-00000",
        title="Breakthrough in Quantum Compute",
        domain="nature.com",
        author="Alice Smith",
        publication_date=datetime.now(timezone.utc),
        credibility_score=0.92,
        credibility_breakdown={"domain": 0.9},
    )
    saved_source = await repo.create_source(source)
    assert saved_source.id == source.id

    # 2. Create Claim Nodes
    node1 = EvidenceNode(
        id=uuid.uuid4(),
        workspace_id=ws_id,
        source_id=saved_source.id,
        claim_text="Quantum error correction threshold reached 99.9%",
        claim_type="FINDING",
        confidence_score=0.98,
        extracted_by_agent="research_agent_1",
        entities=["Quantum Error Correction", "Qubits"],
    )
    node2 = EvidenceNode(
        id=uuid.uuid4(),
        workspace_id=ws_id,
        source_id=saved_source.id,
        claim_text="Physical fidelity limits prevent scaling past 100 qubits",
        claim_type="HYPOTHESIS",
        confidence_score=0.75,
        extracted_by_agent="research_agent_2",
        entities=["Physical Fidelity", "Scaling"],
    )
    saved_node1 = await repo.create_node(node1)
    saved_node2 = await repo.create_node(node2)
    assert saved_node1.claim_type == "FINDING"

    # 3. Create Contradiction Edge
    edge = EvidenceEdge(
        id=uuid.uuid4(),
        workspace_id=ws_id,
        source_node_id=saved_node1.id,
        target_node_id=saved_node2.id,
        relationship_type="CONTRADICTS",
        confidence=0.90,
        reasoning="Node 1 shows 99.9% threshold while Node 2 claims scaling block",
    )
    saved_edge = await repo.create_edge(edge)
    assert saved_edge.relationship_type == "CONTRADICTS"

    # 4. Query Contradictions
    contradictions = await repo.get_contradictions(ws_id)
    assert len(contradictions) == 1
    assert contradictions[0].id == saved_edge.id


@pytest.mark.asyncio
async def test_evidence_api_unauthorized(client: AsyncClient):
    random_ws_id = uuid.uuid4()
    res = await client.get(f"/api/v1/workspaces/{random_ws_id}/evidence/graph")
    assert res.status_code in (401, 404)
