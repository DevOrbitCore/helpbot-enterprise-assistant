"""Identity adapter abstraction and development-only implementation.

SECURITY NOTICE:
`DevelopmentIdentityAdapter` is strictly for local development and automated testing.
It reads tenant/user headers supplied by the host demo app, which MUST NOT be trusted
in production. Production deployments should replace this adapter with a server-side
JWT, OIDC, or signed session token validator.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi import Request

from app.core.exceptions import AuthorizationError


@dataclass(frozen=True)
class AuthenticatedActor:
    """Verified identity scoped to a tenant and user on the server side."""

    tenant_id: str
    user_id: str
    role: str
    is_development_identity: bool = True


class IdentityAdapter(ABC):
    """Boundary interface for resolving caller identity from an HTTP request."""

    @abstractmethod
    def resolve_actor(self, request: Request) -> AuthenticatedActor:
        """Return the authenticated actor or raise AuthorizationError."""


class DevelopmentIdentityAdapter(IdentityAdapter):
    """DEVELOPMENT-ONLY identity adapter reading X-HelpBot-* headers.

    Never enable `HELPBOT_ALLOW_DEV_IDENTITY=true` in a production environment.
    """

    DEFAULT_TENANT = "campusdesk-dev"
    DEFAULT_USER = "demo-student-001"
    DEFAULT_ROLE = "student"

    def __init__(self, allow_dev_identity: bool = True) -> None:
        self._allow_dev_identity = allow_dev_identity

    def resolve_actor(self, request: Request) -> AuthenticatedActor:
        if not self._allow_dev_identity:
            raise AuthorizationError(
                "Development identity adapter is disabled. Configure a verified "
                "production identity adapter before accepting requests.",
                code="identity_adapter_required",
            )

        tenant_id = request.headers.get("X-HelpBot-Tenant-Id", self.DEFAULT_TENANT).strip()
        user_id = request.headers.get("X-HelpBot-User-Id", self.DEFAULT_USER).strip()
        # Role from browser headers is treated as informational only and normalized.
        raw_role = request.headers.get("X-HelpBot-User-Role", self.DEFAULT_ROLE).strip().lower()
        role = raw_role if raw_role in {"student", "ta", "advisor", "staff", "admin"} else "student"

        if not tenant_id or not user_id:
            raise AuthorizationError("Tenant ID and User ID headers must not be empty.")

        return AuthenticatedActor(
            tenant_id=tenant_id[:120],
            user_id=user_id[:120],
            role=role,
            is_development_identity=True,
        )
