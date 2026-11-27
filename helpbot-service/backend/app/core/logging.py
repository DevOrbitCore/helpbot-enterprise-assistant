"""Structured, privacy-aware logging setup for HelpBot.

Logging policy:
- Never log API keys, session tokens, document bodies, or raw user messages.
- Log operational metadata (request ID, status, document ID, latency) only.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

SENSITIVE_PATTERNS = [
    re.compile(r"(AIza[0-9A-Za-z\-_]{20,})"),
    re.compile(r"(Bearer\s+[A-Za-z0-9\-._~+/]+=*)", re.IGNORECASE),
    re.compile(r"(api[_-]?key\s*[=:]\s*[^\s,;]+)", re.IGNORECASE),
]


class RedactingFilter(logging.Filter):
    """Scrubs accidental secret patterns before records are emitted."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            redacted = record.msg
            for pattern in SENSITIVE_PATTERNS:
                redacted = pattern.sub("[REDACTED]", redacted)
            record.msg = redacted
        return True


def configure_logging(logs_dir: Path, level: str = "INFO") -> logging.Logger:
    """Configure console and file logging under helpbot-service/data/logs/."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("helpbot")
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    redactor = RedactingFilter()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(redactor)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(logs_dir / "helpbot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(redactor)
    logger.addHandler(file_handler)

    return logger
