from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm_gateway import LiteLLMGateway, get_litellm_gateway
from app.core.security import decode_token
from app.db.models.user import User
from app.db.session import get_db_session
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.agents.execution_loop import ResearchExecutionLoop
from app.services.agents.fact_extractor import FactExtractorAgent
from app.services.agents.planner import PlannerAgent
from app.services.agents.search_agent import SearchAgent
from app.services.agents.supervisor import SupervisorService
from app.services.agents.synthesizer import SynthesizerAgent
from app.services.auth_service import AuthService
from app.services.document_service import DocumentService
from app.services.evaluations.metrics_service import MetricsService
from app.services.evaluations.ragas_evaluator import RagasEvaluator
from app.services.evidence.evidence_service import EvidenceService
from app.services.ingestion_service import IngestionService
from app.services.reports.report_service import ReportService
from app.services.retrieval.hybrid_search import HybridSearchService
from app.services.retrieval.vector_store import VectorStoreService
from app.services.web_search.search_service import WebSearchEngine
from app.services.workspace_service import WorkspaceService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return UserRepository(session)


async def get_refresh_token_repository(
    session: AsyncSession = Depends(get_db_session),
) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


async def get_workspace_repository(
    session: AsyncSession = Depends(get_db_session),
) -> WorkspaceRepository:
    return WorkspaceRepository(session)


async def get_document_repository(
    session: AsyncSession = Depends(get_db_session),
) -> DocumentRepository:
    return DocumentRepository(session)


async def get_document_chunk_repository(
    session: AsyncSession = Depends(get_db_session),
) -> DocumentChunkRepository:
    return DocumentChunkRepository(session)


async def get_evidence_repository(
    session: AsyncSession = Depends(get_db_session),
) -> EvidenceRepository:
    return EvidenceRepository(session)


async def get_report_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ReportRepository:
    return ReportRepository(session)


async def get_metrics_repository(
    session: AsyncSession = Depends(get_db_session),
) -> MetricsRepository:
    return MetricsRepository(session)


async def get_vector_store_service() -> VectorStoreService:
    return VectorStoreService()


async def get_web_search_engine() -> WebSearchEngine:
    return WebSearchEngine()


async def get_hybrid_search_service(
    vector_store: VectorStoreService = Depends(get_vector_store_service),
    llm_gateway: LiteLLMGateway = Depends(get_litellm_gateway),
) -> HybridSearchService:
    return HybridSearchService(vector_store, llm_gateway)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> AuthService:
    return AuthService(user_repo, refresh_repo)


async def get_workspace_service(
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> WorkspaceService:
    return WorkspaceService(workspace_repo)


async def get_document_service(
    document_repo: DocumentRepository = Depends(get_document_repository),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> DocumentService:
    return DocumentService(document_repo, workspace_repo)


async def get_ingestion_service(
    document_repo: DocumentRepository = Depends(get_document_repository),
    chunk_repo: DocumentChunkRepository = Depends(get_document_chunk_repository),
    vector_store: VectorStoreService = Depends(get_vector_store_service),
    llm_gateway: LiteLLMGateway = Depends(get_litellm_gateway),
) -> IngestionService:
    return IngestionService(
        document_repo=document_repo,
        chunk_repo=chunk_repo,
        vector_store=vector_store,
        llm_gateway=llm_gateway,
    )


async def get_evidence_service(
    evidence_repo: EvidenceRepository = Depends(get_evidence_repository),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> EvidenceService:
    return EvidenceService(
        evidence_repo=evidence_repo,
        workspace_repo=workspace_repo,
    )


async def get_planner_agent(
    llm_gateway: LiteLLMGateway = Depends(get_litellm_gateway),
) -> PlannerAgent:
    return PlannerAgent(llm_gateway)


async def get_fact_extractor_agent(
    llm_gateway: LiteLLMGateway = Depends(get_litellm_gateway),
) -> FactExtractorAgent:
    return FactExtractorAgent(llm_gateway)


async def get_synthesizer_agent(
    llm_gateway: LiteLLMGateway = Depends(get_litellm_gateway),
) -> SynthesizerAgent:
    return SynthesizerAgent(llm_gateway)


async def get_ragas_evaluator(
    llm_gateway: LiteLLMGateway = Depends(get_litellm_gateway),
) -> RagasEvaluator:
    return RagasEvaluator(llm_gateway)


async def get_search_agent(
    hybrid_search: HybridSearchService = Depends(get_hybrid_search_service),
    web_search: WebSearchEngine = Depends(get_web_search_engine),
    llm_gateway: LiteLLMGateway = Depends(get_litellm_gateway),
) -> SearchAgent:
    return SearchAgent(
        hybrid_search=hybrid_search,
        web_search=web_search,
        llm_gateway=llm_gateway,
    )


async def get_supervisor_service(
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    planner_agent: PlannerAgent = Depends(get_planner_agent),
) -> SupervisorService:
    return SupervisorService(workspace_repo, planner_agent)


async def get_execution_loop(
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    evidence_repo: EvidenceRepository = Depends(get_evidence_repository),
    search_agent: SearchAgent = Depends(get_search_agent),
    fact_extractor: FactExtractorAgent = Depends(get_fact_extractor_agent),
) -> ResearchExecutionLoop:
    return ResearchExecutionLoop(
        workspace_repo=workspace_repo,
        evidence_repo=evidence_repo,
        search_agent=search_agent,
        fact_extractor=fact_extractor,
    )


async def get_report_service(
    report_repo: ReportRepository = Depends(get_report_repository),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    evidence_repo: EvidenceRepository = Depends(get_evidence_repository),
    synthesizer: SynthesizerAgent = Depends(get_synthesizer_agent),
) -> ReportService:
    return ReportService(
        report_repo=report_repo,
        workspace_repo=workspace_repo,
        evidence_repo=evidence_repo,
        synthesizer=synthesizer,
    )


async def get_metrics_service(
    metrics_repo: MetricsRepository = Depends(get_metrics_repository),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
    report_repo: ReportRepository = Depends(get_report_repository),
    evidence_repo: EvidenceRepository = Depends(get_evidence_repository),
    evaluator: RagasEvaluator = Depends(get_ragas_evaluator),
) -> MetricsService:
    return MetricsService(
        metrics_repo=metrics_repo,
        workspace_repo=workspace_repo,
        report_repo=report_repo,
        evidence_repo=evidence_repo,
        evaluator=evaluator,
    )


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise credentials_exception
    try:
        user_name_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception
    user = await user_repo.get_by_id(user_name_uuid)
    if not user or not user.is_active:
        raise credentials_exception
    return user
