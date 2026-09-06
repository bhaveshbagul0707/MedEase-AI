from datetime import datetime

from pydantic import EmailStr, Field, field_validator, model_validator

from app.models.enums import StudentProgram
from app.schemas.common import BaseSchema


class UserResponse(BaseSchema):
    id: int
    email: str
    full_name: str
    program: StudentProgram
    year_of_study: int
    avatar_url: str | None = None
    is_active: bool
    is_verified: bool
    created_at: datetime


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    program: StudentProgram
    year_of_study: int = Field(ge=1, le=6)

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, value: str) -> str:
        return value.strip()


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class ForgotPasswordRequest(BaseSchema):
    email: EmailStr


class ResetPasswordRequest(BaseSchema):
    token: str
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def passwords_match(self) -> "ResetPasswordRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class ForgotPasswordResponse(BaseSchema):
    message: str
    reset_token: str | None = None


class VerifyEmailRequest(BaseSchema):
    token: str


class SessionResponse(BaseSchema):
    jti: str
    created_at: datetime
    expires_at: datetime
    revoked: bool
    ip_address: str | None = None
    user_agent: str | None = None
    device_name: str | None = None
    browser: str | None = None
    os: str | None = None
    current: bool = False
    last_used_at: datetime | None = None


class UserUpdateRequest(BaseSchema):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    program: StudentProgram | None = None
    year_of_study: int | None = Field(default=None, ge=1, le=6)
    avatar_url: str | None = Field(default=None, max_length=500)

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class ChangePasswordRequest(BaseSchema):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def passwords_match(self) -> "ChangePasswordRequest":
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
