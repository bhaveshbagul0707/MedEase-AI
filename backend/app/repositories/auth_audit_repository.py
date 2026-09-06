from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_audit import AuthAudit


class AuthAuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, *, event_type: str, user_id: int | None = None, ip_address: str | None = None, user_agent: str | None = None, metadata: str | None = None, created_at: datetime | None = None) -> AuthAudit:
        if created_at is None:
            created_at = datetime.now(timezone.utc)
        entry = AuthAudit(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_=metadata,
            created_at=created_at,
        )
        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)
        return entry
