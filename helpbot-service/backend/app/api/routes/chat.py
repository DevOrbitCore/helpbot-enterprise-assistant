"""Chat and user-scoped conversation history routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.adapters.identity import AuthenticatedActor
from app.api.dependencies import (
    enforce_chat_rate_limit,
    get_chat_service,
    get_current_actor,
)
from app.schemas.contracts import (
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationSummary,
    DeleteResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(enforce_chat_rate_limit)])
def send_chat_message(
    payload: ChatRequest,
    actor: AuthenticatedActor = Depends(get_current_actor),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    return chat_service.handle_chat(actor=actor, payload=payload)


@router.get("/conversations", response_model=list[ConversationSummary])
def list_conversations(
    actor: AuthenticatedActor = Depends(get_current_actor),
    chat_service: ChatService = Depends(get_chat_service),
) -> list[ConversationSummary]:
    return chat_service.list_conversations(actor=actor)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: str,
    actor: AuthenticatedActor = Depends(get_current_actor),
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationDetail:
    return chat_service.get_conversation(actor=actor, conversation_id=conversation_id)


@router.delete("/conversations/{conversation_id}", response_model=DeleteResponse)
def delete_conversation(
    conversation_id: str,
    actor: AuthenticatedActor = Depends(get_current_actor),
    chat_service: ChatService = Depends(get_chat_service),
) -> DeleteResponse:
    deleted_id = chat_service.delete_conversation(actor=actor, conversation_id=conversation_id)
    return DeleteResponse(deleted=True, id=deleted_id)
