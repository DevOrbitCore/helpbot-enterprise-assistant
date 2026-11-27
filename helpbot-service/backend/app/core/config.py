"""Environment-driven configuration for the standalone HelpBot service."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

SERVICE_ROOT = Path(__file__).resolve().parents[3]


def _load_dotenv_file(dotenv_path: Path) -> None:
    """Load key=value pairs from a local .env file without overriding existing env vars."""
    if not dotenv_path.is_file():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def parse_cors_origins(value: str | list[str]) -> list[str]:
    """Normalize a comma-separated string or list of allowed CORS origins."""
    if isinstance(value, str):
        return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]
    return [origin.strip().rstrip("/") for origin in value if origin.strip()]


class Settings(BaseModel):
    """Typed runtime settings loaded from environment variables."""

    env: str = Field(default="development")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8200, ge=1, le=65535)
    public_base_url: str = Field(default="http://127.0.0.1:8200")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://127.0.0.1:5173", "http://localhost:5173"]
    )

    database_url: str = Field(default="")
    data_dir: Path = Field(default_factory=lambda: SERVICE_ROOT / "data")
    max_upload_mb: int = Field(default=10, ge=1, le=100)

    chat_rate_limit_per_min: int = Field(default=30, ge=1, le=1000)
    upload_rate_limit_per_min: int = Field(default=15, ge=1, le=1000)

    ai_provider: str = Field(default="gemini")
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-2.5-flash")

    allow_dev_identity: bool = Field(default=True)

    widget_title: str = Field(default="HelpBot Support Assistant")
    widget_accent_color: str = Field(default="#1d4ed8")

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def conversations_dir(self) -> Path:
        return self.data_dir / "conversations"

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def widget_dir(self) -> Path:
        return SERVICE_ROOT / "widget"

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            if self.database_url.startswith("sqlite:///./"):
                rel = self.database_url.removeprefix("sqlite:///./")
                return f"sqlite:///{(SERVICE_ROOT / rel).as_posix()}"
            return self.database_url
        return f"sqlite:///{(self.data_dir / 'helpbot.db').as_posix()}"

    @property
    def has_valid_gemini_key_format(self) -> bool:
        key = self.gemini_api_key.strip()
        if not key:
            return False
        placeholder_tokens = {"your_gemini_api_key_here", "changeme", "placeholder", "replace_me"}
        return key.lower() not in placeholder_tokens and len(key) >= 10

    def ensure_runtime_directories(self) -> None:
        """Create required runtime directories automatically if absent."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_settings(dotenv_path: Path | None = None) -> Settings:
    """Build a Settings instance from the current environment."""
    _load_dotenv_file(dotenv_path or (SERVICE_ROOT / ".env"))

    raw_data_dir = os.getenv("HELPBOT_DATA_DIR", "").strip()
    if raw_data_dir:
        candidate = Path(raw_data_dir)
        data_dir = candidate if candidate.is_absolute() else (SERVICE_ROOT / candidate).resolve()
    else:
        data_dir = SERVICE_ROOT / "data"

    cors_raw = os.getenv(
        "HELPBOT_CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173"
    )

    settings = Settings(
        env=os.getenv("HELPBOT_ENV", "development").strip(),
        host=os.getenv("HELPBOT_HOST", "127.0.0.1").strip(),
        port=int(os.getenv("HELPBOT_PORT", "8200")),
        public_base_url=os.getenv("HELPBOT_PUBLIC_BASE_URL", "http://127.0.0.1:8200")
        .strip()
        .rstrip("/"),
        cors_origins=parse_cors_origins(cors_raw),
        database_url=os.getenv("HELPBOT_DATABASE_URL", "").strip(),
        data_dir=data_dir,
        max_upload_mb=int(os.getenv("HELPBOT_MAX_UPLOAD_MB", "10")),
        chat_rate_limit_per_min=int(os.getenv("HELPBOT_CHAT_RATE_LIMIT_PER_MIN", "30")),
        upload_rate_limit_per_min=int(os.getenv("HELPBOT_UPLOAD_RATE_LIMIT_PER_MIN", "15")),
        ai_provider=os.getenv("HELPBOT_AI_PROVIDER", "gemini").strip().lower(),
        gemini_api_key=os.getenv("HELPBOT_GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv("HELPBOT_GEMINI_MODEL", "gemini-2.5-flash").strip(),
        allow_dev_identity=_bool_env("HELPBOT_ALLOW_DEV_IDENTITY", True),
        widget_title=os.getenv("HELPBOT_WIDGET_TITLE", "HelpBot Support Assistant").strip(),
        widget_accent_color=os.getenv("HELPBOT_WIDGET_ACCENT_COLOR", "#1d4ed8").strip(),
    )
    settings.ensure_runtime_directories()
    return settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor for FastAPI dependency injection."""
    return load_settings()
