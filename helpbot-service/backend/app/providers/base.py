"""Provider-agnostic AI generation interface for HelpBot."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.contracts import HostContext, RetrievedEvidence


@dataclass(frozen=True)
class ProviderStatus:
    provider: str
    model: str
    configured: bool
    ready: bool
    detail: str


class AIProvider(ABC):
    """Abstract interface isolating LLM vendor SDKs from HelpBot business logic."""

    @abstractmethod
    def get_status(self) -> ProviderStatus:
        """Report whether the provider is configured and ready to serve requests."""

    @abstractmethod
    def generate_grounded_answer(
        self,
        question: str,
        evidence: list[RetrievedEvidence],
        context: HostContext,
    ) -> str:
        """Generate an answer grounded strictly in the provided retrieved evidence."""
