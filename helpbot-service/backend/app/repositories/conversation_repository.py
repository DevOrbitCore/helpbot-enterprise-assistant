"""Tenant- and user-scoped SQLAlchemy repository for chat conversations."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import ChatMessage, Conversation
from app.schemas.contracts import HostContext, RetrievedEvidence


class ConversationRepository:
    """Persists and retrieves conversations strictly within (tenant_id, user_id)."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_conversation(
        self,
        tenant_id: str,
        application_id: str,
        user_id: str,
        title: str,
    ) -> Conversation:
        conversation = Conversation(
            tenant_id=tenant_id,
            application_id=application_id,
            user_id=user_id,
            title=title[:200],
        )
        self._session.add(conversation)
        self._session.flush()
        return conversation

    def get_for_actor(
        self,
        conversation_id: str,
        tenant_id: str,
        user_id: str,
    ) -> Conversation | None:
        stmt = (
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(
                Conversation.id == conversation_id,
                Conversation.tenant_id == tenant_id,
                Conversation.user_id == user_id,
            )
        )
        return self._session.scalars(stmt).first()

    def list_for_actor(
        self,
        tenant_id: str,
        user_id: str,
        limit: int = 50,
    ) -> list[tuple[Conversation, int]]:
        count_subq = (
            select(
                ChatMessage.conversation_id,
                func.count(ChatMessage.id).label("message_count"),
            )
            .group_by(ChatMessage.conversation_id)
            .subquery()
        )
        stmt = (
            select(Conversation, func.coalesce(count_subq.c.message_count, 0))
            .outerjoin(count_subq, Conversation.id == count_subq.c.conversation_id)
            .where(
                Conversation.tenant_id == tenant_id,
                Conversation.user_id == user_id,
            )
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return [(row[0], int(row[1])) for row in self._session.execute(stmt).all()]

    def add_message(
        self,
        conversation: Conversation,
        sender: str,
        content: str,
        sources: list[RetrievedEvidence] | None = None,
        context: HostContext | None = None,
    ) -> ChatMessage:
        message = ChatMessage(
            conversation_id=conversation.id,
            sender=sender,
            content=content,
            sources_json=json.dumps([s.model_dump() for s in (sources or [])]),
            context_snapshot_json=json.dumps(context.model_dump() if context else {}),
        )
        conversation.updated_at = datetime.now(timezone.utc)
        self._session.add(message)
        self._session.flush()
        return message

    def delete_for_actor(
        self,
        conversation_id: str,
        tenant_id: str,
        user_id: str,
    ) -> bool:
        conversation = self.get_for_actor(conversation_id, tenant_id, user_id)
        if conversation is None:
            return False
        self._session.delete(conversation)
        self._session.flush()
        return True
