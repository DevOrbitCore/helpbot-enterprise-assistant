"""Domain exception hierarchy and consistent JSON error responses."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class HelpBotError(Exception):
    """Base application exception mapped to a structured HTTP response."""

    def __init__(self, message: str, status_code: int = 400, code: str = "helpbot_error") -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


class ValidationError(HelpBotError):
    def __init__(self, message: str, code: str = "validation_error") -> None:
        super().__init__(message=message, status_code=400, code=code)


class AuthorizationError(HelpBotError):
    def __init__(self, message: str = "Access denied.", code: str = "forbidden") -> None:
        super().__init__(message=message, status_code=403, code=code)


class NotFoundError(HelpBotError):
    def __init__(self, message: str = "Resource not found.", code: str = "not_found") -> None:
        super().__init__(message=message, status_code=404, code=code)


class RateLimitExceededError(HelpBotError):
    def __init__(
        self,
        message: str = "Too many requests. Please wait a moment and try again.",
        code: str = "rate_limit_exceeded",
    ) -> None:
        super().__init__(message=message, status_code=429, code=code)


class ProviderUnavailableError(HelpBotError):
    def __init__(self, message: str, code: str = "ai_provider_unavailable") -> None:
        super().__init__(message=message, status_code=503, code=code)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach structured exception handlers to the FastAPI application."""

    @app.exception_handler(HelpBotError)
    async def _handle_helpbot_error(_request: Request, exc: HelpBotError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )
