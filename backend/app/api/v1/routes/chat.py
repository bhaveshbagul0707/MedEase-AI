from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatResponse,
    CreateChatRequest,
    MessageResponse,
    PaginationResponse,
    SendMessageRequest,
    UpdateChatRequest,
)
from app.services.medassist_service import MedAssistService
from app.services.openrouter_provider import AIProviderError


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat(
    request: CreateChatRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ChatResponse:
    service = MedAssistService(db)

    chat = await service.create_chat(
        user=current_user,
        title=request.title,
        study_mode=request.study_mode,
        subject=request.subject,
    )

    return ChatResponse.model_validate(chat)


@router.get(
    "",
    response_model=list[ChatResponse],
)
async def get_chats(
    db: DbSession,
    current_user: CurrentUser,
) -> list[ChatResponse]:
    service = MedAssistService(db)

    chats = await service.get_user_chats(current_user)

    return [
        ChatResponse.model_validate(chat)
        for chat in chats
    ]


@router.get(
    "/{chat_id}",
    response_model=ChatHistoryResponse,
)
async def get_chat(
    chat_id: int,
    db: DbSession,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ChatHistoryResponse:
    service = MedAssistService(db)

    try:
        chat = await service.get_chat(
            chat_id=chat_id,
            user=current_user,
        )

        messages, total = await service.get_messages(
            chat_id=chat_id,
            user=current_user,
            limit=limit,
            offset=offset,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ChatHistoryResponse(
        session=ChatResponse.model_validate(chat),
        messages=[
            MessageResponse.model_validate(message)
            for message in messages
        ],
        pagination=PaginationResponse(
            total=total,
            limit=limit,
            offset=offset,
            has_more=offset + len(messages) < total,
        ),
    )


@router.post(
    "/{chat_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    chat_id: int,
    request: SendMessageRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> MessageResponse:
    service = MedAssistService(db)

    try:
        message = await service.send_message(
            chat_id=chat_id,
            user=current_user,
            question=request.content,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except AIProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return MessageResponse.model_validate(message)


@router.patch(
    "/{chat_id}",
    response_model=ChatResponse,
)
async def update_chat(
    chat_id: int,
    request: UpdateChatRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ChatResponse:
    service = MedAssistService(db)

    try:
        chat = await service.update_chat(
            chat_id=chat_id,
            user=current_user,
            title=request.title,
            study_mode=request.study_mode,
            subject=request.subject,
            is_pinned=request.is_pinned,
            is_archived=request.is_archived,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ChatResponse.model_validate(chat)


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chat(
    chat_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    service = MedAssistService(db)

    try:
        await service.delete_chat(
            chat_id=chat_id,
            user=current_user,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc