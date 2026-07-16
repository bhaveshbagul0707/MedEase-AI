from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.security import (
    create_token_pair,
    generate_reset_token,
    get_password_hash,
    get_reset_token_expiry,
    verify_password,
    verify_token_type,
)
from app.models.enums import StudentProgram
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    UserUpdateRequest,
)

settings = get_settings()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    def _to_user_response(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    def _to_token_response(self, user: User) -> TokenResponse:
        tokens = create_token_pair(user.id)
        return TokenResponse(**tokens, user=self._to_user_response(user))

    async def register(self, data: RegisterRequest) -> TokenResponse:
        existing = await self.user_repo.get_by_email(data.email.lower())
        if existing:
            raise ConflictException("Email already registered")

        user = User(
            email=data.email.lower(),
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            program=data.program,
            year_of_study=data.year_of_study,
            is_active=True,
            is_verified=False,
        )
        await self.user_repo.create(user)
        return self._to_token_response(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email.lower())
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")
        return self._to_token_response(user)

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        payload = verify_token_type(refresh_token, "refresh")
        if not payload:
            raise UnauthorizedException("Invalid or expired refresh token")

        user = await self.user_repo.get_by_id(int(payload["sub"]))
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        return self._to_token_response(user)

    async def get_current_user_profile(self, user_id: int) -> UserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return self._to_user_response(user)

    async def update_profile(self, user: User, data: UserUpdateRequest) -> UserResponse:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.user_repo.update(user)
        return self._to_user_response(user)

    async def change_password(self, user: User, data: ChangePasswordRequest) -> None:
        if not verify_password(data.current_password, user.hashed_password):
            raise UnauthorizedException("Current password is incorrect")
        user.hashed_password = get_password_hash(data.new_password)
        await self.user_repo.update(user)

    async def forgot_password(self, email: str) -> ForgotPasswordResponse:
        user = await self.user_repo.get_by_email(email.lower())
        message = "If the email exists, a password reset link has been sent."

        if not user:
            return ForgotPasswordResponse(message=message)

        reset_token = generate_reset_token()
        user.reset_token = reset_token
        user.reset_token_expires = get_reset_token_expiry()
        await self.user_repo.update(user)

        response = ForgotPasswordResponse(message=message)
        if settings.debug:
            response.reset_token = reset_token
        return response

    async def reset_password(self, data: ResetPasswordRequest) -> TokenResponse:
        user = await self.user_repo.get_by_reset_token(data.token)
        if not user:
            raise UnauthorizedException("Invalid or expired reset token")

        expires = user.reset_token_expires
        if expires and expires.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise UnauthorizedException("Reset token has expired")

        user.hashed_password = get_password_hash(data.password)
        user.reset_token = None
        user.reset_token_expires = None
        await self.user_repo.update(user)
        return self._to_token_response(user)

    async def authenticate_google_user(
        self,
        *,
        google_id: str,
        email: str,
        full_name: str,
        avatar_url: str | None = None,
    ) -> TokenResponse:
        user = await self.user_repo.get_by_google_id(google_id)
        if not user:
            user = await self.user_repo.get_by_email(email.lower())
            if user:
                user.google_id = google_id
                if avatar_url and not user.avatar_url:
                    user.avatar_url = avatar_url
                user.is_verified = True
                await self.user_repo.update(user)
            else:
                user = User(
                    email=email.lower(),
                    hashed_password=get_password_hash(generate_reset_token()),
                    full_name=full_name,
                    program=StudentProgram.MBBS,
                    year_of_study=1,
                    avatar_url=avatar_url,
                    google_id=google_id,
                    is_active=True,
                    is_verified=True,
                )
                await self.user_repo.create(user)

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        return self._to_token_response(user)
