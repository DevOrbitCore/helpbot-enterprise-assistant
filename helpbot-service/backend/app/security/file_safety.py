"""Safe upload validation, extension allowlist, and path-traversal protection."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from app.core.exceptions import ValidationError

SUPPORTED_EXTENSIONS: dict[str, set[str]] = {
    ".pdf": {"application/pdf", "application/octet-stream"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/octet-stream",
        "application/zip",
    },
    ".md": {"text/markdown", "text/plain", "text/x-markdown", "application/octet-stream"},
    ".html": {"text/html", "application/xhtml+xml", "text/plain", "application/octet-stream"},
    ".htm": {"text/html", "application/xhtml+xml", "text/plain", "application/octet-stream"},
    ".txt": {"text/plain", "application/octet-stream"},
    ".vtt": {"text/vtt", "text/plain", "application/octet-stream"},
    ".srt": {"application/x-subrip", "text/srt", "text/plain", "application/octet-stream"},
}

EXTENSION_TO_SOURCE_TYPE: dict[str, str] = {
    ".pdf": "document",
    ".docx": "document",
    ".md": "document",
    ".html": "document",
    ".htm": "document",
    ".txt": "document",
    ".vtt": "transcript",
    ".srt": "transcript",
}

_SAFE_BASENAME_RE = re.compile(r"[^A-Za-z0-9._ -]+")


def sanitize_display_filename(raw_filename: str | None) -> str:
    """Strip directory components and unsafe characters for safe display metadata."""
    if not raw_filename:
        raise ValidationError("A filename is required for upload.", code="missing_filename")
    base = Path(raw_filename).name.strip()
    if not base or base in {".", ".."}:
        raise ValidationError("Invalid filename supplied.", code="invalid_filename")
    cleaned = _SAFE_BASENAME_RE.sub("_", base)
    return cleaned[:200]


def validate_upload_file(
    raw_filename: str | None,
    content_type: str | None,
    content_bytes: bytes,
    max_upload_bytes: int,
) -> tuple[str, str, str, str]:
    """Validate an uploaded file and return (display_name, extension, mime, source_type)."""
    display_name = sanitize_display_filename(raw_filename)
    extension = Path(display_name).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValidationError(
            f"Unsupported file type '{extension or 'none'}'. Supported formats: {allowed}.",
            code="unsupported_file_type",
        )

    if not content_bytes:
        raise ValidationError("Uploaded file is empty.", code="empty_file")

    if len(content_bytes) > max_upload_bytes:
        limit_mb = max_upload_bytes / (1024 * 1024)
        raise ValidationError(
            f"Uploaded file exceeds the {limit_mb:.1f} MB size limit.",
            code="file_too_large",
        )

    normalized_mime = (content_type or "application/octet-stream").split(";")[0].strip().lower()
    allowed_mimes = SUPPORTED_EXTENSIONS[extension]
    if normalized_mime not in allowed_mimes:
        raise ValidationError(
            f"MIME type '{normalized_mime}' is not valid for '{extension}' files.",
            code="invalid_mime_type",
        )

    source_type = EXTENSION_TO_SOURCE_TYPE[extension]
    return display_name, extension, normalized_mime, source_type


def generate_safe_storage_path(uploads_dir: Path, extension: str) -> tuple[str, Path]:
    """Generate a UUID-based filename strictly inside uploads_dir."""
    uploads_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{extension}"
    resolved_root = uploads_dir.resolve()
    target = (resolved_root / stored_name).resolve()
    if resolved_root not in target.parents:
        raise ValidationError("Resolved storage path escaped the upload directory.")
    return stored_name, target


def resolve_controlled_file_path(uploads_dir: Path, stored_filename: str) -> Path:
    """Safely resolve an existing stored filename inside uploads_dir."""
    safe_name = Path(stored_filename).name
    resolved_root = uploads_dir.resolve()
    target = (resolved_root / safe_name).resolve()
    if resolved_root not in target.parents:
        raise ValidationError("Invalid stored file path.", code="invalid_path")
    return target
