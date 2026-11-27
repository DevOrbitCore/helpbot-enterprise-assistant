"""Tests for health, AI status, missing-key behavior, widget-config, and security headers."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.providers.gemini_provider import GeminiAIProvider


def test_health_and_security_headers(client: TestClient) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "helpbot-service"
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert "microphone=()" in resp.headers["permissions-policy"]


def test_missing_gemini_key_boots_cleanly_and_reports_status(tmp_path: Path) -> None:
    settings = Settings(
        env="test",
        database_url=f"sqlite:///{(tmp_path / 'no_key.db').as_posix()}",
        data_dir=tmp_path / "data",
        ai_provider="gemini",
        gemini_api_key="",
    )
    app = create_app(settings=settings, ai_provider=GeminiAIProvider(settings))
    with TestClient(app) as test_client:
        status_resp = test_client.get("/api/ai/status")
        assert status_resp.status_code == 200
        payload = status_resp.json()
        assert payload["provider"] == "gemini"
        assert payload["configured"] is False
        assert payload["ready"] is False


def test_widget_config_and_cors_allowlist(client: TestClient) -> None:
    resp = client.get(
        "/api/widget-config",
        headers={"Origin": "http://127.0.0.1:5173"},
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://127.0.0.1:5173"
    data = resp.json()
    assert data["api_base_url"] == "http://127.0.0.1:8200"
    assert data["features"]["voice_interaction"] is False
    assert data["features"]["semantic_retrieval"] is False
    assert data["features"]["image_knowledge"] is False
    assert data["features"]["video_tutorials"] is False


def test_disallowed_cors_origin_not_reflected(client: TestClient) -> None:
    resp = client.get(
        "/api/widget-config",
        headers={"Origin": "https://untrusted-site.example"},
    )
    assert resp.status_code == 200
    assert "access-control-allow-origin" not in resp.headers
