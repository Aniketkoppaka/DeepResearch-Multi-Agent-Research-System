from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.evidence import router as evidence_router
from app.api.v1.execution import router as execution_router
from app.api.v1.health import router as health_router
from app.api.v1.plans import router as plans_router
from app.api.v1.search import router as search_router
from app.api.v1.workspaces import router as workspaces_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(workspaces_router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(documents_router, prefix="/workspaces", tags=["documents"])
api_router.include_router(search_router, prefix="/workspaces", tags=["search"])
api_router.include_router(evidence_router, prefix="/workspaces", tags=["evidence"])
api_router.include_router(plans_router, prefix="/workspaces", tags=["plans"])
api_router.include_router(execution_router, prefix="/workspaces", tags=["execution"])
