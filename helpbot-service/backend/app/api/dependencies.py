"""FastAPI dependency wiring for database sessions, identity, providers, and rate limits."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.adapters.identity import AuthenticatedActor, IdentityAdapter
from app.core.config import Settings
from app.database.session import DatabaseManager
from app.providers.base import AIProvider
from app.security.rate_limit import InMemoryRateLimiter
from app.services.chat_service import ChatService
from app.services.knowledge_service import KnowledgeService
from app.services.retrieval_service import KnowledgeRetriever


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_db_session(request: Request) -> Generator[Session, None, None]:
    db_manager: DatabaseManager = request.app.state.db_manager
    yield from db_manager.get_session()


def get_ai_provider(request: Request) -> AIProvider:
    return request.app.state.ai_provider


def get_retriever(request: Request) -> KnowledgeRetriever:
    return request.app.state.retriever


def get_current_actor(request: Request) -> AuthenticatedActor:
    adapter: IdentityAdapter = request.app.state.identity_adapter
    return adapter.resolve_actor(request)


def enforce_chat_rate_limit(
    request: Request,
    actor: AuthenticatedActor = Depends(get_current_actor),
) -> None:
    limiter: InMemoryRateLimiter = request.app.state.chat_rate_limiter
    limiter.check(f"chat:{actor.tenant_id}:{actor.user_id}")


def enforce_upload_rate_limit(
    request: Request,
    actor: AuthenticatedActor = Depends(get_current_actor),
) -> None:
    limiter: InMemoryRateLimiter = request.app.state.upload_rate_limiter
    limiter.check(f"upload:{actor.tenant_id}:{actor.user_id}")


def get_chat_service(
    session: Session = Depends(get_db_session),
    retriever: KnowledgeRetriever = Depends(get_retriever),
    ai_provider: AIProvider = Depends(get_ai_provider),
) -> ChatService:
    return ChatService(session=session, retriever=retriever, ai_provider=ai_provider)


def get_knowledge_service(
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_app_settings),
) -> KnowledgeService:
    return KnowledgeService(session=session, settings=settings)
