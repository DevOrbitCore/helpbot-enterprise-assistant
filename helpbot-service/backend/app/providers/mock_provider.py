"""Deterministic offline AIProvider for automated tests and no-key local demos."""

from __future__ import annotations

from app.providers.base import AIProvider, ProviderStatus
from app.schemas.contracts import HostContext, RetrievedEvidence


class MockAIProvider(AIProvider):
    """Produces deterministic grounded summaries from retrieved evidence without network calls."""

    def __init__(self, model: str = "mock-deterministic-v1") -> None:
        self._model = model

    def get_status(self) -> ProviderStatus:
        return ProviderStatus(
            provider="mock",
            model=self._model,
            configured=True,
            ready=True,
            detail="Deterministic mock AI provider active (offline mode).",
        )

    def generate_grounded_answer(
        self,
        question: str,
        evidence: list[RetrievedEvidence],
        context: HostContext,
    ) -> str:
        if not evidence:
            return "I could not find this in the available HelpBot documents."

        top = evidence[0]
        location = top.page_or_section or top.timestamp_range or "document"
        return (
            f"Based on '{top.title}' ({top.file_name}, {location}): "
            f"{top.excerpt}"
        )
