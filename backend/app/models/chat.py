from typing import TYPE_CHECKING, List

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import MessageRole, StudyMode
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="New Chat",
    )

    study_mode: Mapped[StudyMode] = mapped_column(
        Enum(StudyMode, name="study_mode", native_enum=False),
        nullable=False,
        default=StudyMode.LEARN,
    )

    subject: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_pinned: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    is_archived: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="chat_sessions",
    )

    messages: Mapped[List["Message"]] = relationship(
        back_populates="chat_session",
        cascade="all, delete-orphan",
    )


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, name="message_role", native_enum=False),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    chat_session: Mapped["ChatSession"] = relationship(
        back_populates="messages",
    )