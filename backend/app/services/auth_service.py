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
from app.repositories.refresh_token_repository import RefreshTokenRepository
from datetime import datetime

from app.models.enums import StudentProgram
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.auth_audit_repository import AuthAuditRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    UserUpdateRequest,
    VerifyEmailRequest,
    SessionResponse,
)
from app.core.config import get_settings
from app.repositories.refresh_token_repository import RefreshTokenRepository
from datetime import timedelta
from app.core.security import generate_reset_token
from jose import JWTError
import json

settings = get_settings()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.rt_repo = RefreshTokenRepository(db)
        self.audit_repo = AuthAuditRepository(db)

    def _to_user_response(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    async def _to_token_response(self, user: User, *, ip_address: str | None = None, user_agent: str | None = None) -> TokenResponse:
        # create_token_pair now returns (tokens_dict, refresh_jti, refresh_expires)
        tokens, refresh_jti, refresh_expires = create_token_pair(user.id)
        # Persist refresh token jti for rotation / revocation
        now = datetime.now(timezone.utc)
        await self.rt_repo.create(jti=refresh_jti, user_id=user.id, expires_at=refresh_expires, created_at=now, ip_address=ip_address, user_agent=user_agent)
        return TokenResponse(**tokens, user=self._to_user_response(user))

    async def register(self, data: RegisterRequest, *, ip_address: str | None = None, user_agent: str | None = None) -> TokenResponse:
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
        # Email verification token
        verification_token = generate_reset_token()
        user.email_verification_token = verification_token
        user.email_verification_expires = datetime.now(timezone.utc) + timedelta(hours=settings.verification_token_expiry_hours)

        await self.user_repo.create(user)
        # Audit register
        await self.audit_repo.create(event_type="REGISTER", user_id=user.id, ip_address=ip_address, user_agent=user_agent, metadata=None)
        token_resp = await self._to_token_response(user, ip_address=ip_address, user_agent=user_agent)
        # In debug, include verification token in returned data by adding to metadata field? For now tests don't expect it; return token as usual
        return token_resp

    async def login(self, data: LoginRequest, *, ip_address: str | None = None, user_agent: str | None = None) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email.lower())
        if not user:
            # Audit failed login with unknown user
            await self.audit_repo.create(event_type="LOGIN_FAILURE", user_id=None, ip_address=ip_address, user_agent=user_agent, metadata=json.dumps({"email": data.email}))
            raise UnauthorizedException("Invalid email or password")

        # Check if account is locked
        if user.locked_until and user.locked_until.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
            await self.audit_repo.create(event_type="ACCOUNT_LOCKED", user_id=user.id, ip_address=ip_address, user_agent=user_agent, metadata=None)
            raise UnauthorizedException("Account is temporarily locked due to multiple failed login attempts")

        if not verify_password(data.password, user.hashed_password):
            # Increment failed attempts atomically
            new_count = await self.user_repo.increment_failed_logins(user.id, delta=1)
            await self.audit_repo.create(event_type="LOGIN_FAILURE", user_id=user.id, ip_address=ip_address, user_agent=user_agent, metadata=json.dumps({"fail_count": new_count}))
            if new_count >= settings.max_failed_login_attempts:
                lock_until = datetime.now(timezone.utc) + timedelta(minutes=settings.lockout_minutes)
                await self.user_repo.set_locked_until(user.id, lock_until)
                await self.audit_repo.create(event_type="ACCOUNT_LOCKED", user_id=user.id, ip_address=ip_address, user_agent=user_agent, metadata=json.dumps({"locked_until": lock_until.isoformat()}))
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        # Successful login: reset failed attempts and locked_until
        await self.user_repo.reset_failed_logins(user.id)
        await self.audit_repo.create(event_type="LOGIN_SUCCESS", user_id=user.id, ip_address=ip_address, user_agent=user_agent, metadata=None)
        return await self._to_token_response(user, ip_address=ip_address, user_agent=user_agent)

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        payload = verify_token_type(refresh_token, "refresh")
        if not payload:
            raise UnauthorizedException("Invalid or expired refresh token")

        jti = payload.get("jti")
        if not jti:
            raise UnauthorizedException("Refresh token missing identifier")

        user_id = int(payload.get("sub"))
        rt_repo = RefreshTokenRepository(self.db)

        now = datetime.now(timezone.utc)
        # Atomically revoke the refresh token if it is active and not expired
        revoked = await rt_repo.revoke_if_active(jti, user_id, now=now)
        if not revoked:
            # Token not found, already revoked, expired, or doesn't belong to user
            raise UnauthorizedException("Refresh token revoked or not found")

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        # Issue a new refresh token (rotation)
        tokens, new_jti, new_expires = create_token_pair(user.id)
        # Audit token refresh
        await self.audit_repo.create(event_type="TOKEN_REFRESH", user_id=user.id, ip_address=None, user_agent=None, metadata=json.dumps({"old_jti": jti, "new_jti": new_jti}))
        await rt_repo.create(jti=new_jti, user_id=user.id, expires_at=new_expires, created_at=now)
        return TokenResponse(**tokens, user=self._to_user_response(user))

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
        # Revoke all refresh tokens after password change
        await self.rt_repo.revoke_all_for_user(user.id)
        await self.audit_repo.create(event_type="PASSWORD_CHANGED", user_id=user.id, ip_address=None, user_agent=None, metadata=None)

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
        await self.audit_repo.create(event_type="PASSWORD_RESET", user_id=user.id, ip_address=None, user_agent=None, metadata=None)
        return await self._to_token_response(user)

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

        return await self._to_token_response(user)

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        payload = verify_token_type(refresh_token, "refresh")
        if not payload:
            raise UnauthorizedException("Invalid or expired refresh token")
        jti = payload.get("jti")
        if not jti:
            raise UnauthorizedException("Refresh token missing identifier")
        user_id = int(payload.get("sub"))
        rt_repo = RefreshTokenRepository(self.db)
        # Revoke atomically only if it belongs to the user and is active
        now = datetime.now(timezone.utc)
        revoked = await rt_repo.revoke_if_active(jti, user_id, now=now)
        if not revoked:
            # If it wasn't active, still treat as success (idempotent)
            return
        # Audit successful revoke (logout)
        await self.audit_repo.create(event_type="LOGOUT", user_id=user_id, ip_address=None, user_agent=None, metadata=json.dumps({"jti": jti}))

    async def verify_email(self, token: str) -> None:
        user = await self.user_repo.get_by_email_token(token)
        if not user:
            raise UnauthorizedException("Invalid or expired verification token")
        if user.email_verification_expires and user.email_verification_expires.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise UnauthorizedException("Verification token has expired")
        user.is_verified = True
        user.email_verification_token = None
        user.email_verification_expires = None
        await self.user_repo.update(user)
        await self.audit_repo.create(event_type="EMAIL_VERIFIED", user_id=user.id, ip_address=None, user_agent=None, metadata=None)

    async def list_sessions(self, user: User, current_jti: str | None = None) -> list[SessionResponse]:
        sessions = await self.rt_repo.list_by_user(user.id, active_only=False)
        result: list[SessionResponse] = []
        for s in sessions:
            device_name = None
            browser = None
            os = None
            ua = s.user_agent or ""
            # naive parsing
            if "Windows" in ua:
                os = "Windows"
            elif "Macintosh" in ua or "Mac OS" in ua:
                os = "macOS"
            elif "Linux" in ua:
                os = "Linux"
            if "Chrome" in ua:
                browser = "Chrome"
            elif "Firefox" in ua:
                browser = "Firefox"
            elif "Safari" in ua and "Chrome" not in ua:
                browser = "Safari"
            if "Mobile" in ua:
                device_name = "Mobile"
            else:
                device_name = "Desktop"
            result.append(
                SessionResponse(
                    jti=s.jti,
                    created_at=s.created_at,
                    expires_at=s.expires_at,
                    revoked=s.revoked,
                    ip_address=s.ip_address,
                    user_agent=s.user_agent,
                    device_name=device_name,
                    browser=browser,
                    os=os,
                    current=(s.jti == current_jti),
                    last_used_at=s.last_used_at,
                )
            )
        return result

    async def revoke_session(self, user: User, jti: str) -> None:
        # Ensure session belongs to user
        session = await self.rt_repo.get_by_jti(jti)
        if not session or session.user_id != user.id:
            raise NotFoundException("Session not found")
        await self.rt_repo.revoke_by_jti(jti)
        await self.audit_repo.create(event_type="LOGOUT", user_id=user.id, ip_address=session.ip_address, user_agent=session.user_agent, metadata=json.dumps({"jti": jti}))

    async def revoke_all_sessions(self, user: User) -> None:
        await self.rt_repo.revoke_all_for_user(user.id)
        await self.audit_repo.create(event_type="LOGOUT_ALL_DEVICES", user_id=user.id, ip_address=None, user_agent=None, metadata=None)
