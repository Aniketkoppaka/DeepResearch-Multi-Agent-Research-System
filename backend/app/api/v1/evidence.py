import uuid
from typing import List

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.deps import (
    get_current_user,
    get_evidence_service,
)
from app.db.models.user import User
from app.schemas.evidence import (
    EvidenceEdgeCreate,
    EvidenceEdgeResponse,
    EvidenceGraphResponse,
    EvidenceNodeCreate,
    EvidenceNodeResponse,
    EvidenceSourceCreate,
    EvidenceSourceResponse,
)
from app.services.evidence.evidence_service import EvidenceService

router = APIRouter()


@router.get(
    "/{workspace_id}/evidence/graph",
    response_model=EvidenceGraphResponse,
    status_code=status.HTTP_200_OK,
)
async def get_evidence_graph(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    evidence_service: EvidenceService = Depends(get_evidence_service),
) -> EvidenceGraphResponse:
    """Retrieve full Relational Evidence Knowledge Graph for workspace."""
    return await evidence_service.get_graph(workspace_id, current_user.id)


@router.post(
    "/{workspace_id}/evidence/sources",
    response_model=EvidenceSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_evidence_source(
    workspace_id: uuid.UUID,
    request: EvidenceSourceCreate,
    current_user: User = Depends(get_current_user),
    evidence_service: EvidenceService = Depends(get_evidence_service),
) -> EvidenceSourceResponse:
    """Create a verified evidence source with automated credibility scoring."""
    source = await evidence_service.create_source(workspace_id, current_user.id, request)
    return EvidenceSourceResponse.model_validate(source)


@router.post(
    "/{workspace_id}/evidence/nodes",
    response_model=EvidenceNodeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_evidence_node(
    workspace_id: uuid.UUID,
    request: EvidenceNodeCreate,
    current_user: User = Depends(get_current_user),
    evidence_service: EvidenceService = Depends(get_evidence_service),
) -> EvidenceNodeResponse:
    """Create an evidence claim node linked to an evidence source."""
    node = await evidence_service.create_node(workspace_id, current_user.id, request)
    return EvidenceNodeResponse.model_validate(node)


@router.post(
    "/{workspace_id}/evidence/edges",
    response_model=EvidenceEdgeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_evidence_edge(
    workspace_id: uuid.UUID,
    request: EvidenceEdgeCreate,
    current_user: User = Depends(get_current_user),
    evidence_service: EvidenceService = Depends(get_evidence_service),
) -> EvidenceEdgeResponse:
    """Link two evidence claim nodes with a typed relationship (SUPPORTS, CONTRADICTS, etc.)."""
    edge = await evidence_service.create_edge(workspace_id, current_user.id, request)
    return EvidenceEdgeResponse.model_validate(edge)


@router.post(
    "/{workspace_id}/search/web",
    response_model=List[EvidenceSourceResponse],
    status_code=status.HTTP_200_OK,
)
async def search_web_and_index(
    workspace_id: uuid.UUID,
    query: str = Query(..., min_length=1),
    max_results: int = Query(default=5, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    evidence_service: EvidenceService = Depends(get_evidence_service),
) -> List[EvidenceSourceResponse]:
    """Execute live web search and auto-index as scored evidence sources."""
    sources = await evidence_service.search_web_and_index(
        workspace_id=workspace_id,
        user_id=current_user.id,
        query=query,
        max_results=max_results,
    )
    return [EvidenceSourceResponse.model_validate(s) for s in sources]
