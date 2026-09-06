from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import DbSession, CurrentUser
from app.services.quiz_service import QuizService
from app.schemas.common import APIResponse, MessageResponse
from app.schemas.flashcard import FlashcardResponse
from app.repositories.base import BaseRepository
from app.models.flashcard import Flashcard

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.post("/generate/from-flashcards", response_model=APIResponse[dict])
async def generate_from_flashcards(db: DbSession, current_user: CurrentUser, count: int = 10):
    # pick recent flashcards for user
    repo = BaseRepository(Flashcard, db)
    from sqlalchemy import select
    stmt = select(repo.model).where(repo.model.user_id == current_user.id).limit(count)
    res = await db.execute(stmt)
    fcs = res.scalars().all()
    if not fcs:
        raise HTTPException(status_code=404, detail="No flashcards found")
    svc = QuizService(db)
    quiz = await svc.generate_from_flashcards(current_user.id, fcs, title=f"Auto quiz {current_user.id}")
    return APIResponse(message="Quiz generated", data={"quiz_id": quiz.id})


@router.get("/{quiz_id}", response_model=APIResponse[dict])
async def get_quiz(quiz_id: int, db: DbSession, current_user: CurrentUser):
    svc = QuizService(db)
    quiz = await svc.get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    # simple serialization
    items = []
    for q in quiz.questions:
        items.append({"id": q.id, "prompt": q.question_text, "answer": q.correct_answer})
    return APIResponse(message="Quiz retrieved", data={"id": quiz.id, "questions": items})


@router.post("/{quiz_id}/submit", response_model=APIResponse[dict])
async def submit_quiz(quiz_id: int, payload: dict, db: DbSession, current_user: CurrentUser):
    answers = payload.get("answers", [])
    svc = QuizService(db)
    result = await svc.submit(quiz_id, current_user.id, answers)
    return APIResponse(message="Quiz submitted", data={"result_id": result.id, "score": result.score, "total": result.total_questions})
