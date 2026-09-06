import json
from typing import List
from app.repositories.base import BaseRepository
from app.models.quiz import Quiz, QuizQuestion, QuizResult
from app.models.enums import QuizType, DifficultyLevel, QuestionType
from app.repositories.base import BaseRepository
from datetime import datetime

class QuizService:
    def __init__(self, db):
        self.db = db
        self.quiz_repo = BaseRepository(Quiz, db)
        self.q_repo = BaseRepository(QuizQuestion, db)
        self.result_repo = BaseRepository(QuizResult, db)

    async def generate_from_flashcards(self, user_id: int, flashcards: List, title: str | None = None) -> Quiz:
        quiz = Quiz(user_id=user_id, title=title or f"Auto quiz {user_id}", quiz_type=QuizType.MCQ, difficulty=DifficultyLevel.MEDIUM, question_count=0)
        await self.quiz_repo.create(quiz)
        questions = []
        order = 0
        for fc in flashcards:
            q = QuizQuestion(quiz_id=quiz.id, question_text=fc.front, correct_answer=fc.back, question_type=QuestionType.MCQ, options=None, order_index=order)
            await self.q_repo.create(q)
            order += 1
            questions.append(q)
        quiz.question_count = len(questions)
        await self.quiz_repo.update(quiz)
        # refresh quiz
        await self.db.refresh(quiz)
        return quiz

    async def get_quiz(self, quiz_id: int) -> Quiz | None:
        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        stmt = select(self.quiz_repo.model).where(self.quiz_repo.model.id == quiz_id).options(joinedload(self.quiz_repo.model.questions))
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def submit(self, quiz_id: int, user_id: int, answers: List[dict]) -> QuizResult:
        quiz = await self.get_quiz(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")
        total = len(answers)
        correct = 0
        for ans in answers:
            qid = ans.get("question_id")
            resp = ans.get("answer")
            q = await self.q_repo.get_by_id(qid)
            if q and q.correct_answer.strip().lower() == str(resp).strip().lower():
                correct += 1
        result = QuizResult(quiz_id=quiz_id, user_id=user_id, score=float(correct), total_questions=total, correct_answers=correct, time_taken_seconds=None, answers=None)
        await self.result_repo.create(result)
        return result
