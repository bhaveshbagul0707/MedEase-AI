from fastapi import APIRouter

from app import __version__
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.files import router as files_router
from app.api.v1.routes.knowledge import router as knowledge_router
from app.api.v1.routes.notes import router as notes_router
from app.api.v1.routes.flashcards import router as flashcards_router
from app.schemas.common import APIResponse, HealthResponse
from app.api.v1.routes.attendance import router as attendance_router
from app.api.v1.routes.study_plans import router as study_plans_router
from app.api.v1.routes.community import router as community_router
from app.api.v1.routes.clinical_cases import router as clinical_cases_router

router = APIRouter()


@router.get("/health", response_model=APIResponse[HealthResponse])
async def health_check() -> APIResponse[HealthResponse]:
    return APIResponse(
        message="MedEase AI is running",
        data=HealthResponse(
            status="healthy",
            version=__version__,
            environment="development",
        ),
    )


router.include_router(auth_router)
router.include_router(files_router)
router.include_router(knowledge_router)
router.include_router(notes_router)
router.include_router(flashcards_router)
from app.api.v1.routes.reviews import router as reviews_router
router.include_router(reviews_router)
from app.api.v1.routes.quiz import router as quiz_router
router.include_router(quiz_router)
from app.api.v1.routes.flashcard_generator import router as flashcard_generator_router
router.include_router(flashcard_generator_router)
from app.api.v1.routes.tutor import router as tutor_router
router.include_router(tutor_router)
from app.api.v1.routes.analytics import router as analytics_router
router.include_router(analytics_router)
router.include_router(attendance_router)
router.include_router(study_plans_router)
router.include_router(community_router)
router.include_router(clinical_cases_router)
# keep ordering consistent
