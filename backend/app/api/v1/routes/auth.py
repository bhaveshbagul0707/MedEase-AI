from urllib.parse import urlencode

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.oauth import oauth
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    UserUpdateRequest,
)
from app.schemas.common import APIResponse, MessageResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


def _auth_service(db: DbSession) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=APIResponse[TokenResponse])
async def register(data: RegisterRequest, db: DbSession) -> APIResponse[TokenResponse]:
    result = await _auth_service(db).register(data)
    return APIResponse(message="Registration successful", data=result)


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(data: LoginRequest, db: DbSession) -> APIResponse[TokenResponse]:
    result = await _auth_service(db).login(data)
    return APIResponse(message="Login successful", data=result)


@router.post("/logout", response_model=APIResponse[MessageResponse])
async def logout(_current_user: CurrentUser) -> APIResponse[MessageResponse]:
    return APIResponse(
        message="Logged out successfully",
        data=MessageResponse(message="Please discard your tokens on the client."),
    )


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh_token(data: RefreshTokenRequest, db: DbSession) -> APIResponse[TokenResponse]:
    result = await _auth_service(db).refresh_tokens(data.refresh_token)
    return APIResponse(message="Token refreshed", data=result)


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_me(current_user: CurrentUser) -> APIResponse[UserResponse]:
    return APIResponse(
        message="Profile retrieved",
        data=UserResponse.model_validate(current_user),
    )


@router.patch("/me", response_model=APIResponse[UserResponse])
async def update_me(
    data: UserUpdateRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> APIResponse[UserResponse]:
    result = await _auth_service(db).update_profile(current_user, data)
    return APIResponse(message="Profile updated", data=result)


@router.post("/change-password", response_model=APIResponse[MessageResponse])
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> APIResponse[MessageResponse]:
    await _auth_service(db).change_password(current_user, data)
    return APIResponse(
        message="Password changed successfully",
        data=MessageResponse(message="Password changed successfully"),
    )


@router.post("/forgot-password", response_model=APIResponse[ForgotPasswordResponse])
async def forgot_password(
    data: ForgotPasswordRequest, db: DbSession
) -> APIResponse[ForgotPasswordResponse]:
    result = await _auth_service(db).forgot_password(data.email)
    return APIResponse(message=result.message, data=result)


@router.post("/reset-password", response_model=APIResponse[TokenResponse])
async def reset_password(
    data: ResetPasswordRequest, db: DbSession
) -> APIResponse[TokenResponse]:
    result = await _auth_service(db).reset_password(data)
    return APIResponse(message="Password reset successful", data=result)


@router.get("/google")
async def google_login(request: Request):
    if not settings.google_client_id or not settings.google_client_secret:
        raise AppException("Google OAuth is not configured", status_code=503)
    return await oauth.google.authorize_redirect(request, settings.google_redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: DbSession):
    if not settings.google_client_id or not settings.google_client_secret:
        raise AppException("Google OAuth is not configured", status_code=503)

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as exc:
        raise AppException("Google authentication failed", status_code=400) from exc

    user_info = token.get("userinfo")
    if not user_info:
        raise AppException("Failed to retrieve Google user info", status_code=400)

    google_id = user_info.get("sub")
    email = user_info.get("email")
    if not google_id or not email:
        raise AppException("Google account missing required fields", status_code=400)

    auth_result = await _auth_service(db).authenticate_google_user(
        google_id=google_id,
        email=email,
        full_name=user_info.get("name", email.split("@")[0]),
        avatar_url=user_info.get("picture"),
    )

    params = urlencode(
        {
            "access_token": auth_result.access_token,
            "refresh_token": auth_result.refresh_token,
        }
    )
    redirect_url = f"{settings.frontend_url}/auth/google/callback?{params}"
    return RedirectResponse(url=redirect_url)
