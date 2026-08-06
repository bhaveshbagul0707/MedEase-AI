from fastapi import APIRouter

from app import __version__
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.chat import router as chat_router
from app.schemas.common import APIResponse, HealthResponse

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
router.include_router(chat_router)