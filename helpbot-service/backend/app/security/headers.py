"""HTTP security headers middleware for local development and hardened defaults.

Note on Permissions-Policy:
Microphone access is explicitly disabled (`microphone=()`) in this baseline.
The future voice interaction student assignment may update this header only after
explicit security review and configuration opt-in.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attaches baseline defensive HTTP response headers."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "microphone=(), camera=(), geolocation=()",
        )
        return response
