"""Shared pytest fixtures for HelpBot backend tests (zero network calls)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.providers.mock_provider import MockAIProvider


@pytest.fixture()
def test_settings(tmp_path: Path) -> Settings:
    data_dir = tmp_path / "data"
    settings = Settings(
        env="test",
        public_base_url="http://127.0.0.1:8200",
        cors_origins=["http://127.0.0.1:5173"],
        database_url=f"sqlite:///{(data_dir / 'test_helpbot.db').as_posix()}",
        data_dir=data_dir,
        max_upload_mb=2,
        ai_provider="mock",
        gemini_api_key="",
        allow_dev_identity=True,
    )
    settings.ensure_runtime_directories()
    return settings


@pytest.fixture()
def client(test_settings: Settings) -> TestClient:
    app = create_app(settings=test_settings, ai_provider=MockAIProvider())
    with TestClient(app) as test_client:
        yield test_client
