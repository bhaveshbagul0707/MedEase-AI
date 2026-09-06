from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from sqlalchemy import update


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, *, jti: str, user_id: int, expires_at: datetime, created_at: datetime | None = None, ip_address: str | None = None, user_agent: str | None = None) -> RefreshToken:
        if created_at is None:
            created_at = datetime.now(timezone.utc)
        token = RefreshToken(
            jti=jti,
            user_id=user_id,
            created_at=created_at,
            expires_at=expires_at,
            revoked=False,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(token)
        await self.db.flush()
        await self.db.refresh(token)
        return token

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self.db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int, *, active_only: bool = True, skip: int = 0, limit: int = 50) -> list[RefreshToken]:
        query = select(RefreshToken).where(RefreshToken.user_id == user_id)
        if active_only:
            query = query.where(RefreshToken.revoked.is_(False))
        query = query.offset(skip).limit(limit).order_by(RefreshToken.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def revoke_if_active(self, jti: str, user_id: int, now: datetime | None = None) -> bool:
        """Atomically revoke the refresh token if it is active (not revoked) and not expired, and belongs to user_id.
        Returns True if a row was updated (revoked), False otherwise."""
        if now is None:
            now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.jti == jti,
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > now,
            )
            .values(revoked=True)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        try:
            return result.rowcount > 0
        except Exception:
            # Some DB backends don't populate rowcount reliably; fall back to checking existence
            existing = await self.get_by_jti(jti)
            return bool(existing and not existing.revoked and existing.user_id == user_id and existing.expires_at > now)

    async def revoke_by_jti(self, jti: str) -> None:
        await self.db.execute(
            update(RefreshToken).where(RefreshToken.jti == jti).values(revoked=True)
        )
        await self.db.flush()

    async def revoke_all_for_user(self, user_id: int) -> None:
        await self.db.execute(
            update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True)
        )
        await self.db.flush()

    async def mark_used(self, jti: str, last_used_at: datetime | None = None) -> None:
        if last_used_at is None:
            last_used_at = datetime.now(timezone.utc)
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.jti == jti)
            .values(last_used_at=last_used_at)
        )
        await self.db.flush()
