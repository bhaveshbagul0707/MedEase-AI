from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import MessageRole, StudyMode


# ---------- Chat ----------

class CreateChatRequest(BaseModel):
    title: str = Field(default="New Chat", min_length=1, max_length=255)
    study_mode: StudyMode = StudyMode.LEARN
    subject: str | None = Field(default=None, max_length=100)


class UpdateChatRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    study_mode: StudyMode | None = None
    subject: str | None = Field(default=None, max_length=100)
    is_pinned: bool | None = None
    is_archived: bool | None = None


class ChatResponse(BaseModel):
    id: int
    title: str
    study_mode: StudyMode
    subject: str | None
    is_pinned: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# ---------- Messages ----------

class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10_000)


class MessageResponse(BaseModel):
    id: int
    role: MessageRole
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class PaginationResponse(BaseModel):
    total: int
    limit: int
    offset: int
    has_more: bool

# ---------- Chat History ----------

class ChatHistoryResponse(BaseModel):
    session: ChatResponse
    messages: list[MessageResponse]
    pagination: PaginationResponse