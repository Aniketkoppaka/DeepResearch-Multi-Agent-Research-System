import uuid
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        jti: str,
        user_id: uuid.UUID,
        expires_at: datetime,
    ) -> RefreshToken:
        token_rec = RefreshToken(
            jti=jti,
            user_id=user_id,
            expires_at=expires_at,
            is_revoked=False,
        )
        self.session.add(token_rec)
        await self.session.commit()
        await self.session.refresh(token_rec)
        return token_rec

    async def get_by_jti(self, jti: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.jti == jti)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def revoke(self, jti: str) -> bool:
        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.jti == jti)
            .values(is_revoked=True, revoked_at=now)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> int:
        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)  # noqa: E712

            .values(is_revoked=True, revoked_at=now)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount
