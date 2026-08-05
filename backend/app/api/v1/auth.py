from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.api.v1.deps import get_auth_service, get_current_user, get_user_repository
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    return await auth_service.register_user(user_in)

@router.post("/login", response_model=TokenResponse)
async def login(
    response: Response,
    cred: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    user, access_token, refresh_token = await auth_service.authenticate_user(cred)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False, samesite="lax",
        max_age=7 * 24 * 3600
    )
    return TokenResponse(access_token=access_token, user=user)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    repo: UserRepository = Depends(get_user_repository)
) -> TokenResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token payload"
        )
    try:
        user_id = UUID(str(user_id_str))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID format"
        )
    user = await repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive"
        )
    new_access = create_access_token(data={"sub": str(user.id)})
    new_refresh = create_refresh_token(data={"sub": str(user.id)})
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False, samesite="lax",
        max_age=7 * 24 * 3600
    )
    return TokenResponse(access_token=new_access, user=UserResponse.model_validate(user))

@router.post("/logout")
async def logout(response: Response) -> dict[str, Any]:
    response.delete_cookie("bearer_token")
    response.delete_cookie("refresh_token")
    return {"success": True, "message": "Logout successful"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
