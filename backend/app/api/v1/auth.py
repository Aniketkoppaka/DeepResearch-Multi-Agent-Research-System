from typing import Dict, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status, Header
from app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.api.v1.deps import get_auth_service, get_current_user
from app.db.models.user import User
from app.core.config import settings
from app.core.rate_limiter import RateLimiter
from app.core.security import decode_token

router = APIRouter()
strict_limiter = RateLimiter(limit=5, window_seconds=60)


def verify_csrf_header(x: Optional[str] = Header(None, alias="X-CSRF-Token")) -> None:
    if settings.ENVIRONMENT != "test" and not x:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing X-CSRF-Token header",
        )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(strict_limiter)],
)

async def register(
    user_in: UserRegister,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    return await auth_service.register(user_in)

@router.post("/login", response_model=TokenResponse, dependencies=[Depends(strict_limiter)])
async def login(
    cred: UserLogin,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    access_token, refresh_token, user = await auth_service.authenticate(cred)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=(settings.ENVIRONMENT == "production"),
        samesite="lax",
        path="/api/v1/auth",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )

@router.post(
    "/refresh",
    response_model=TokenResponse,
    dependencies=[Depends(strict_limiter), Depends(verify_csrf_header)],
)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token cookie is missing",
        )
    new_access, new_refresh = await auth_service.refresh_token(refresh_token)
    payload = decode_token(new_access)
    user_id = payload.get("sub") if payload else None
    user = await auth_service.user_repo.get_by_id(uuid.UUID(user_id)) if user_id else None
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=(settings.ENVIRONMENT == "production"),
        samesite="lax",
        path="/api/v1/auth",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )
    return TokenResponse(
        access_token=new_access,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", dependencies=[Depends(verify_csrf_header)])
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> Dict[str, bool]:
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await auth_service.revoke_refresh_token(refresh_token)
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")
    return {"success": True}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
