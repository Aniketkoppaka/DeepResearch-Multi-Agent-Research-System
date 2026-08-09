import uuid
from typing import Tuple
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.schemas.auth import UserRegister, UserLogin, UserResponse
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class AuthService:
    def __init__(self, user_repo: UserRepository, refresh_repo: RefreshTokenRepository) -> None:
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo

    async def register(self, user_in: UserRegister) -> UserResponse:
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        hashed_password = get_password_hash(user_in.password)
        user = await self.user_repo.create(
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
        )
        return UserResponse.model_validate(user)

    async def authenticate(self, cred: UserLogin) -> Tuple[str, str, UserResponse]:
        user = await self.user_repo.get_by_email(cred.email)
        if not user or not verify_password(cred.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user account",
            )
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token, jti, expires_at = create_refresh_token({"sub": str(user.id)})
        await self.refresh_repo.create(
            jti=jti,
            user_id=user.id,
            expires_at=expires_at,
        )
        return access_token, refresh_token, UserResponse.model_validate(user)

    async def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        jti = payload.get("jti")
        user_id_str = payload.get("sub")
        if not jti or not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload",
            )
        token_rec = await self.refresh_repo.get_by_jti(jti)
        if not token_rec or token_rec.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked or is invalid",
            )
        if token_rec.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )
        await self.refresh_repo.revoke(jti)
        user = await self.user_repo.get_by_id(uuid.UUID(user_id_str))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        new_access_token = create_access_token({"sub": str(user.id)})
        new_refresh_token, new_jti, new_expires_at = create_refresh_token({"sub": str(user.id)})
        await self.refresh_repo.create(
            jti=new_jti,
            user_id=user.id,
            expires_at=new_expires_at,
        )
        return new_access_token, new_refresh_token

    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        payload = decode_token(refresh_token)
        if payload and payload.get("type") == "refresh":
            jti = payload.get("jti")
            if jti:
                return await self.refresh_repo.revoke(jti)
        return False
