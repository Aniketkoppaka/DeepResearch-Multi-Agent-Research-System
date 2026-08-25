import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.deps import (
    get_current_user,
    get_hybrid_search_service,
    get_workspace_repository,
)
from app.db.models.user import User
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.search import SearchQueryResponse, SearchRequest, SearchResultResponse
from app.services.retrieval.hybrid_search import HybridSearchService

router = APIRouter()


@router.post(
    "/{workspace_id}/search",
    response_model=SearchQueryResponse,
    status_code=status.HTTP_200_OK,
)
async def search_workspace_documents(
    workspace_id: uuid.UUID,
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    search_service: HybridSearchService = Depends(get_hybrid_search_service),
) -> SearchQueryResponse:
    """
    Execute hybrid dense + sparse retrieval across documents in workspace with IDOR isolation.
    """
    workspace = await workspace_repo.get_by_id_and_user(workspace_id, current_user.id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    results = await search_service.search(
        query=request.query,
        workspace_id=workspace_id,
        document_ids=request.document_ids,
        limit=request.limit,
    )

    return SearchQueryResponse(
        query=request.query,
        total_results=len(results),
        results=[SearchResultResponse.model_validate(r) for r in results],
    )
