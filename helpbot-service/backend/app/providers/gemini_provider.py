"""Google Gemini AIProvider using the supported `google-genai` Python SDK.

The API key and model name are read from Settings (environment variables) only.
When the key is missing, placeholder-valued, or invalid, the service remains bootable
and reports a clear configuration status without crashing.
"""

from __future__ import annotations

import logging

from app.core.config import Settings
from app.core.exceptions import ProviderUnavailableError
from app.providers.base import AIProvider, ProviderStatus
from app.schemas.contracts import HostContext, RetrievedEvidence

logger = logging.getLogger("helpbot.providers.gemini")

SYSTEM_INSTRUCTIONS = (
    "You are HelpBot, a concise and accurate support assistant. "
    "Answer the user's question using ONLY the provided documentation excerpts. "
    "Do not rely on outside knowledge or invent policies, dates, or fees. "
    "If the provided excerpts do not contain enough information to answer, reply: "
    "'I could not find this in the available HelpBot documents.'"
)


class GeminiAIProvider(AIProvider):
    """Gemini provider backed by the official `google-genai` SDK."""

    def __init__(self, settings: Settings) -> None:
        self._model = settings.gemini_model
        self._api_key = settings.gemini_api_key
        self._has_valid_key = settings.has_valid_gemini_key_format
        self._client = None
        self._sdk_available = False

        try:
            from google import genai  # type: ignore[import-not-found]

            self._sdk_available = True
            if self._has_valid_key:
                self._client = genai.Client(api_key=self._api_key)
        except ImportError:
            self._sdk_available = False
        except Exception:
            logger.warning("Gemini client initialization failed; check HELPBOT_GEMINI_API_KEY.")
            self._client = None

    def get_status(self) -> ProviderStatus:
        if not self._sdk_available:
            return ProviderStatus(
                provider="gemini",
                model=self._model,
                configured=self._has_valid_key,
                ready=False,
                detail="The google-genai package is not installed in this Python environment.",
            )
        if not self._has_valid_key or self._client is None:
            return ProviderStatus(
                provider="gemini",
                model=self._model,
                configured=False,
                ready=False,
                detail=(
                    "HELPBOT_GEMINI_API_KEY is not configured. Set a valid Gemini API key "
                    "in helpbot-service/.env to enable live AI responses."
                ),
            )
        return ProviderStatus(
            provider="gemini",
            model=self._model,
            configured=True,
            ready=True,
            detail="Gemini provider is configured and ready.",
        )

    def generate_grounded_answer(
        self,
        question: str,
        evidence: list[RetrievedEvidence],
        context: HostContext,
    ) -> str:
        status = self.get_status()
        if not status.ready or self._client is None:
            raise ProviderUnavailableError(status.detail)

        evidence_blocks = []
        for idx, item in enumerate(evidence, start=1):
            location = item.page_or_section or item.timestamp_range or "Document"
            evidence_blocks.append(
                f"[Source {idx}: {item.title} ({item.file_name}, {location})]\n{item.excerpt}"
            )

        prompt = (
            f"Host context: application={context.application_id}, "
            f"module={context.module_id}, screen={context.screen_id}, locale={context.locale}\n\n"
            f"Retrieved HelpBot documentation:\n"
            + "\n\n".join(evidence_blocks)
            + f"\n\nUser question:\n{question}\n\n"
            "Respond clearly and concisely using only the retrieved documentation above."
        )

        try:
            from google.genai import types  # type: ignore[import-not-found]

            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTIONS,
                    temperature=0.2,
                ),
            )
            text = (getattr(response, "text", None) or "").strip()
            if not text:
                return "I could not find this in the available HelpBot documents."
            return text
        except Exception as exc:
            logger.error("Gemini generation request failed (%s).", type(exc).__name__)
            raise ProviderUnavailableError(
                "The configured Gemini provider could not complete the request. "
                "Verify your API key, model name, and network connectivity."
            ) from exc
