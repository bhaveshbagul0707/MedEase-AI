from sqlalchemy import select
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
