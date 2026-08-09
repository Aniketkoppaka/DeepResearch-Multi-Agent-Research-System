from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db_session
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.document_repository import DocumentRepository
from app.services.auth_service import AuthService
from app.services.workspace_service import WorkspaceService
from app.services.document_service import DocumentService
from app.core.security import decode_token
from app.db.models.user import User

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
