"""Chat orchestration service combining retrieval, grounded generation, and persistence."""

from __future__ import annotations

import json
import logging

from sqlalchemy.orm import Session

from app.adapters.identity import AuthenticatedActor
from app.core.exceptions import NotFoundError
from app.models.entities import ChatMessage, Conversation
from app.providers.base import AIProvider
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.contracts import (
    ChatMessageRead,
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationSummary,
    HostContext,
    RetrievedEvidence,
)
from app.services.retrieval_service import KnowledgeRetriever

logger = logging.getLogger("helpbot.services.chat")

NO_EVIDENCE_RESPONSE = "I could not find this in the available HelpBot documents."


class ChatService:
    """Orchestrates grounded Q&A while enforcing tenant and user boundaries."""

    def __init__(
        self,
        session: Session,
        retriever: KnowledgeRetriever,
        ai_provider: AIProvider,
    ) -> None:
        self._session = session
        self._conversations = ConversationRepository(session)
        self._knowledge = KnowledgeRepository(session)
        self._retriever = retriever
        self._ai_provider = ai_provider

    def handle_chat(self, *, actor: AuthenticatedActor, payload: ChatRequest) -> ChatResponse:
        # Enforce server-resolved tenant and user identity over client payload context.
        scoped_context = HostContext(
            tenant_id=actor.tenant_id,
            application_id=payload.context.application_id,
            user_id=actor.user_id,
            role=actor.role,
            module_id=payload.context.module_id,
            screen_id=payload.context.screen_id,
            route=payload.context.route,
            page_title=payload.context.page_title,
            locale=payload.context.locale,
        )

        conversation: Conversation | None = None
        if payload.conversation_id:
            conversation = self._conversations.get_for_actor(
                conversation_id=payload.conversation_id,
                tenant_id=actor.tenant_id,
                user_id=actor.user_id,
            )
            if conversation is None:
                raise NotFoundError("Conversation not found for the current user.")
        else:
            title = payload.message.strip()[:80] or "New conversation"
            conversation = self._conversations.create_conversation(
                tenant_id=actor.tenant_id,
                application_id=scoped_context.application_id,
                user_id=actor.user_id,
                title=title,
            )

        user_msg = self._conversations.add_message(
            conversation=conversation,
            sender="user",
            content=payload.message.strip(),
            context=scoped_context,
        )

        tenant_docs = self._knowledge.list_documents(tenant_id=actor.tenant_id)
        evidence = self._retriever.retrieve(
            query=payload.message,
            documents=tenant_docs,
            context=scoped_context,
            top_k=3,
        )

        provider_status = self._ai_provider.get_status()
        if not evidence:
            answer_text = NO_EVIDENCE_RESPONSE
            grounded = False
            provider_used = "no-evidence-guard"
        else:
            answer_text = self._ai_provider.generate_grounded_answer(
                question=payload.message.strip(),
                evidence=evidence,
                context=scoped_context,
            )
            grounded = True
            provider_used = f"{provider_status.provider}:{provider_status.model}"

        assistant_msg = self._conversations.add_message(
            conversation=conversation,
            sender="assistant",
            content=answer_text,
            sources=evidence,
            context=scoped_context,
        )
        self._session.commit()

        logger.info(
            "Chat turn persisted conversation_id=%s grounded=%s sources=%d",
            conversation.id,
            grounded,
            len(evidence),
        )

        return ChatResponse(
            conversation_id=conversation.id,
            user_message=self._to_message_schema(user_msg),
            assistant_message=self._to_message_schema(assistant_msg),
            sources=evidence,
            grounded=grounded,
            provider_used=provider_used,
        )

    def list_conversations(self, *, actor: AuthenticatedActor) -> list[ConversationSummary]:
        rows = self._conversations.list_for_actor(
            tenant_id=actor.tenant_id,
            user_id=actor.user_id,
        )
        return [
            ConversationSummary(
                id=conv.id,
                tenant_id=conv.tenant_id,
                application_id=conv.application_id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=count,
            )
            for conv, count in rows
        ]

    def get_conversation(
        self,
        *,
        actor: AuthenticatedActor,
        conversation_id: str,
    ) -> ConversationDetail:
        conv = self._conversations.get_for_actor(
            conversation_id=conversation_id,
            tenant_id=actor.tenant_id,
            user_id=actor.user_id,
        )
        if conv is None:
            raise NotFoundError("Conversation not found for the current user.")

        return ConversationDetail(
            id=conv.id,
            tenant_id=conv.tenant_id,
            application_id=conv.application_id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=[self._to_message_schema(msg) for msg in conv.messages],
        )

    def delete_conversation(self, *, actor: AuthenticatedActor, conversation_id: str) -> str:
        deleted = self._conversations.delete_for_actor(
            conversation_id=conversation_id,
            tenant_id=actor.tenant_id,
            user_id=actor.user_id,
        )
        if not deleted:
            raise NotFoundError("Conversation not found for the current user.")
        self._session.commit()
        return conversation_id

    @staticmethod
    def _to_message_schema(msg: ChatMessage) -> ChatMessageRead:
        try:
            raw_sources = json.loads(msg.sources_json) if msg.sources_json else []
            sources = [RetrievedEvidence.model_validate(item) for item in raw_sources]
        except Exception:
            sources = []
        return ChatMessageRead(
            id=msg.id,
            sender="assistant" if msg.sender == "assistant" else "user",
            content=msg.content,
            sources=sources,
            created_at=msg.created_at,
        )
