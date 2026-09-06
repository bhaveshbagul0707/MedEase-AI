from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subject import Subject
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def increment_failed_logins(self, user_id: int, delta: int = 1) -> int:
        # Atomic increment of failed_login_attempts
        await self.db.execute(
            update(User).where(User.id == user_id).values(failed_login_attempts=(User.failed_login_attempts + delta))
        )
        await self.db.flush()
        user = await self.get_by_id(user_id)
        return user.failed_login_attempts if user else 0

    async def reset_failed_logins(self, user_id: int) -> None:
        await self.db.execute(
            update(User).where(User.id == user_id).values(failed_login_attempts=0, locked_until=None)
        )
        await self.db.flush()

    async def set_locked_until(self, user_id: int, locked_until):
        await self.db.execute(
            update(User).where(User.id == user_id).values(locked_until=locked_until)
        )
        await self.db.flush()

    async def get_by_email_token(self, token: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email_verification_token == token))
        return result.scalar_one_or_none()

    async def get_by_google_id(self, google_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.google_id == google_id))
        return result.scalar_one_or_none()

    async def get_by_reset_token(self, token: str) -> User | None:
        result = await self.db.execute(select(User).where(User.reset_token == token))
        return result.scalar_one_or_none()


class SubjectRepository(BaseRepository[Subject]):
    def __init__(self, db: AsyncSession):
        super().__init__(Subject, db)

    async def get_by_code(self, code: str) -> Subject | None:
        result = await self.db.execute(select(Subject).where(Subject.code == code))
        return result.scalar_one_or_none()

    async def get_by_program(
        self,
        program: str,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Subject]:
        result = await self.db.execute(
            select(Subject)
            .where((Subject.program == program) | (Subject.program.is_(None)))
            .offset(skip)
            .limit(limit)
            .order_by(Subject.name)
        )
        return list(result.scalars().all())
