"""Convenience launcher for local HelpBot Service development."""

from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings  # noqa: E402


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "development",
        app_dir=str(BACKEND_DIR),
    )


if __name__ == "__main__":
    main()
