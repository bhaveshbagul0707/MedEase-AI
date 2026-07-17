from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import MessageRole, StudyMode


# ---------- Chat ----------

class CreateChatRequest(BaseModel):
    title: str = Field(..., max_length=255)
    study_mode: StudyMode
    subject: str | None = None


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
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: int
    role: MessageRole
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


# ---------- Chat History ----------

class ChatHistoryResponse(BaseModel):
    session: ChatResponse
    messages: list[MessageResponse]