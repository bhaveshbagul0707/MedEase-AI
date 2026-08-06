from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatSession, Message
from app.models.enums import MessageRole, StudyMode
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.services.ai_engine import AIEngine


class MedAssistService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_repository = ChatRepository(db)
        self.ai_engine = AIEngine()

    async def create_chat(
        self,
        *,
        user: User,
        study_mode: StudyMode = StudyMode.LEARN,
        subject: str | None = None,
        title: str = "New Chat",
    ) -> ChatSession:
        chat = ChatSession(
            user_id=user.id,
            title=title,
            study_mode=study_mode,
            subject=subject,
        )

        return await self.chat_repository.create(chat)

    async def get_user_chats(
        self,
        user: User,
    ) -> list[ChatSession]:
        return await self.chat_repository.get_user_chats(user.id)

    async def get_chat(
        self,
        *,
        chat_id: int,
        user: User,
    ) -> ChatSession:
        chat = await self.chat_repository.get_chat(
            chat_id=chat_id,
            user_id=user.id,
        )

        if chat is None:
            raise ValueError("Chat not found")

        return chat

    async def get_messages(
        self,
        *,
        chat_id: int,
        user: User,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Message], int]:
        chat = await self.get_chat(
            chat_id=chat_id,
            user=user,
        )

        messages = await self.chat_repository.get_messages_paginated(
            chat.id,
            limit=limit,
            offset=offset,
        )

        total = await self.chat_repository.count_messages(chat.id)

        return messages, total

    def _generate_chat_title(self, question: str) -> str:
        cleaned = " ".join(question.strip().split())

        prefixes = [
            "what is ",
            "what are ",
            "explain ",
            "tell me about ",
            "describe ",
            "define ",
        ]

        lower = cleaned.lower()

        for prefix in prefixes:
            if lower.startswith(prefix):
                cleaned = cleaned[len(prefix):]
                break

        cleaned = cleaned.rstrip("?.!")

        if not cleaned:
            return "New Chat"

        if len(cleaned) > 50:
            cleaned = cleaned[:47].rstrip() + "..."

        return cleaned.title()

    async def send_message(
        self,
        *,
        chat_id: int,
        user: User,
        question: str,
    ) -> Message:
        question = question.strip()

        if not question:
            raise ValueError("Message cannot be empty")

        chat = await self.get_chat(
            chat_id=chat_id,
            user=user,
        )

        # Get previous messages for AI context
        previous_messages = await self.chat_repository.get_messages(chat.id)

        # Keep only latest 10 messages as AI context
        recent_messages = previous_messages[-10:]

        # Automatically generate title from first question
        if not previous_messages and chat.title == "New Chat":
            chat.title = self._generate_chat_title(question)
            await self.chat_repository.update(chat)

        # Save user message
        user_message = Message(
            session_id=chat.id,
            role=MessageRole.USER,
            content=question,
        )

        await self.chat_repository.create_message(user_message)

        # Generate AI response
        ai_response = await self.ai_engine.generate_response(
            study_mode=chat.study_mode,
            question=question,
            program=user.program.value,
            year=user.year_of_study,
            conversation_history=recent_messages,
        )

        # Save assistant response
        assistant_message = Message(
            session_id=chat.id,
            role=MessageRole.ASSISTANT,
            content=ai_response,
        )

        return await self.chat_repository.create_message(
            assistant_message
        )

    async def update_chat(
        self,
        *,
        chat_id: int,
        user: User,
        title: str | None = None,
        study_mode: StudyMode | None = None,
        subject: str | None = None,
        is_pinned: bool | None = None,
        is_archived: bool | None = None,
    ) -> ChatSession:
        chat = await self.get_chat(
            chat_id=chat_id,
            user=user,
        )

        if title is not None:
            title = title.strip()

            if not title:
                raise ValueError("Chat title cannot be empty")

            chat.title = title

        if study_mode is not None:
            chat.study_mode = study_mode

        if subject is not None:
            subject = subject.strip()

            if not subject:
                raise ValueError("Subject cannot be empty")

            chat.subject = subject

        if is_pinned is not None:
            chat.is_pinned = is_pinned

        if is_archived is not None:
            chat.is_archived = is_archived

        return await self.chat_repository.update(chat)

    async def delete_chat(
        self,
        *,
        chat_id: int,
        user: User,
    ) -> None:
        chat = await self.get_chat(
            chat_id=chat_id,
            user=user,
        )

        await self.chat_repository.delete_chat(chat)