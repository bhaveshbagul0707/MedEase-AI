from datetime import datetime, timedelta, timezone
from typing import Optional

from app.repositories.flashcard_repository import FlashcardRepository
from app.models.flashcard_schedule import FlashcardSchedule
from app.repositories.base import BaseRepository


class SpacedRepetitionService:
    def __init__(self, db):
        self.db = db
        self.fc_repo = FlashcardRepository(db)
        self.schedule_repo = BaseRepository(FlashcardSchedule, db)

    async def ensure_schedule(self, flashcard_id: int):
        sched = await self.schedule_repo.get_by_id(flashcard_id)
        # schedule_repo.get_by_id expects schedule id, so we must query by flashcard_id
        from sqlalchemy import select
        stmt = select(self.schedule_repo.model).where(self.schedule_repo.model.flashcard_id == flashcard_id)
        res = await self.db.execute(stmt)
        sched = res.scalars().first()
        if not sched:
            now = datetime.now(timezone.utc)
            sched = FlashcardSchedule(flashcard_id=flashcard_id, ef=2.5, interval_days=1, repetition=0, next_review_at=now)
            await self.schedule_repo.create(sched)
        return sched

    async def get_due_flashcards(self, user_id: int, as_of: Optional[datetime] = None):
        as_of = as_of or datetime.now(timezone.utc)
        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        stmt = (
            select(self.schedule_repo.model)
            .join(self.fc_repo.model)
            .where(self.fc_repo.model.user_id == user_id)
            .where(self.schedule_repo.model.next_review_at <= as_of)
            .options(joinedload(self.schedule_repo.model.flashcard))
        )
        res = await self.db.execute(stmt)
        scheds = res.scalars().all()
        return scheds

    async def record_review(self, flashcard_id: int, correct: bool) -> FlashcardSchedule:
        sched = await self.ensure_schedule(flashcard_id)
        # SM-2 algorithm simplified
        if correct:
            sched.repetition += 1
            if sched.repetition == 1:
                sched.interval_days = 1
            elif sched.repetition == 2:
                sched.interval_days = 6
            else:
                sched.interval_days = int(round(sched.interval_days * sched.ef))
            sched.ef = max(1.3, sched.ef + (0.1 - (5 - 5) * (0.08 + (5 - 5) * 0.02)))
        else:
            sched.repetition = 0
            sched.interval_days = 1
            sched.ef = max(1.3, sched.ef - 0.2)
        sched.next_review_at = datetime.now(timezone.utc) + timedelta(days=sched.interval_days)
        await self.schedule_repo.update(sched)
        return sched
