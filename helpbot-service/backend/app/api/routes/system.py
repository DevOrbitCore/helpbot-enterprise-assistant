"""System health, AI provider status, and embeddable widget configuration routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_ai_provider, get_app_settings
from app.core.config import Settings
from app.providers.base import AIProvider
from app.schemas.contracts import AIStatusResponse, HealthResponse, WidgetConfigResponse

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health_check(settings: Settings = Depends(get_app_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="helpbot-service",
        version="0.1.0",
        environment=settings.env,
    )


@router.get("/ai/status", response_model=AIStatusResponse)
def ai_status(ai_provider: AIProvider = Depends(get_ai_provider)) -> AIStatusResponse:
    status = ai_provider.get_status()
    return AIStatusResponse(
        provider=status.provider,
        model=status.model,
        configured=status.configured,
        ready=status.ready,
        detail=status.detail,
    )


@router.get("/widget-config", response_model=WidgetConfigResponse)
def widget_config(
    settings: Settings = Depends(get_app_settings),
    ai_provider: AIProvider = Depends(get_ai_provider),
) -> WidgetConfigResponse:
    status = ai_provider.get_status()
    return WidgetConfigResponse(
        api_base_url=settings.public_base_url,
        widget_script_url=f"{settings.public_base_url}/widget/src/helpbot-widget.js",
        widget_title=settings.widget_title,
        accent_color=settings.widget_accent_color,
        ai_ready=status.ready,
        features={
            "semantic_retrieval": False,
            "image_knowledge": False,
            "video_tutorials": False,
            "voice_interaction": False,
        },
        identity_mode="development-only" if settings.allow_dev_identity else "verified",
    )
