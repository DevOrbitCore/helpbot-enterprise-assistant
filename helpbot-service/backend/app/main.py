"""FastAPI application factory for the standalone HelpBot Service."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.adapters.identity import DevelopmentIdentityAdapter, IdentityAdapter
from app.api.routes import chat, knowledge, system
from app.core.config import Settings, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.database.session import DatabaseManager
from app.providers.base import AIProvider
from app.providers.gemini_provider import GeminiAIProvider
from app.providers.mock_provider import MockAIProvider
from app.security.headers import SecurityHeadersMiddleware
from app.security.rate_limit import InMemoryRateLimiter
from app.services.retrieval_service import KeywordKnowledgeRetriever, KnowledgeRetriever


def _build_default_provider(settings: Settings) -> AIProvider:
    if settings.ai_provider == "mock":
        return MockAIProvider()
    return GeminiAIProvider(settings=settings)


def create_app(
    *,
    settings: Settings | None = None,
    ai_provider: AIProvider | None = None,
    retriever: KnowledgeRetriever | None = None,
    identity_adapter: IdentityAdapter | None = None,
) -> FastAPI:
    """Create and wire a self-contained HelpBot FastAPI application."""
    resolved_settings = settings or get_settings()
    resolved_settings.ensure_runtime_directories()
    configure_logging(resolved_settings.logs_dir)

    app = FastAPI(
        title="HelpBot Standalone Service",
        version="0.1.0",
        description=(
            "Embeddable support assistant backend with knowledge ingestion, "
            "deterministic keyword retrieval baseline, and tenant-scoped chat history."
        ),
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-HelpBot-Tenant-Id",
            "X-HelpBot-User-Id",
            "X-HelpBot-User-Role",
        ],
    )

    db_manager = DatabaseManager(resolved_settings.resolved_database_url)
    db_manager.create_tables()

    app.state.settings = resolved_settings
    app.state.db_manager = db_manager
    app.state.ai_provider = ai_provider or _build_default_provider(resolved_settings)
    app.state.retriever = retriever or KeywordKnowledgeRetriever()
    app.state.identity_adapter = identity_adapter or DevelopmentIdentityAdapter(
        allow_dev_identity=resolved_settings.allow_dev_identity
    )
    app.state.chat_rate_limiter = InMemoryRateLimiter(
        max_requests=resolved_settings.chat_rate_limit_per_min,
        window_seconds=60,
    )
    app.state.upload_rate_limiter = InMemoryRateLimiter(
        max_requests=resolved_settings.upload_rate_limit_per_min,
        window_seconds=60,
    )

    register_exception_handlers(app)

    app.include_router(system.router)
    app.include_router(chat.router)
    app.include_router(knowledge.router)

    # Strictly serve ONLY public widget assets — never data/, uploads/, logs/, or .env.
    if resolved_settings.widget_dir.is_dir():
        app.mount(
            "/widget",
            StaticFiles(directory=str(resolved_settings.widget_dir)),
            name="widget-assets",
        )

    return app


app = create_app()
