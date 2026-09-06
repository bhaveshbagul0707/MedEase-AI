from datetime import datetime, timedelta, timezone
from app.repositories.base import BaseRepository
from app.models.flashcard import Flashcard
from app.models.flashcard_schedule import FlashcardSchedule
from app.models.quiz import QuizResult

class AnalyticsService:
    def __init__(self, db):
        self.db = db
        self.fc_repo = BaseRepository(Flashcard, db)
        self.sched_repo = BaseRepository(FlashcardSchedule, db)
        self.quiz_result_repo = BaseRepository(QuizResult, db)

    async def study_progress(self, user_id: int):
        # total flashcards
        from sqlalchemy import select, func
        total = (await self.db.execute(select(func.count()).select_from(Flashcard).where(Flashcard.user_id == user_id))).scalar_one()
        learned = (await self.db.execute(select(func.count()).select_from(Flashcard).where(Flashcard.user_id == user_id).where(Flashcard.is_learned == True))).scalar_one()
        # due reviews
        now = datetime.now(timezone.utc)
        due = (await self.db.execute(select(func.count()).select_from(FlashcardSchedule).join(Flashcard).where(Flashcard.user_id == user_id).where(FlashcardSchedule.next_review_at <= now))).scalar_one()
        # quizzes last 7 days
        week_ago = now - timedelta(days=7)
        quiz_count = (await self.db.execute(select(func.count()).select_from(QuizResult).where(QuizResult.user_id == user_id))).scalar_one()
        return {
            "total_flashcards": total,
            "learned_flashcards": learned,
            "due_reviews": due,
            "quizzes_taken": quiz_count,
        }
