"""Retrieval abstraction and deterministic keyword baseline.

EXTENSION SEAM (Student Assignment #1 — Context-Aware Semantic Retrieval):
Replace or wrap `KeywordKnowledgeRetriever` with a chunk-based semantic or hybrid
retriever implementing `KnowledgeRetriever`. Keep `RetrievedEvidence` stable so
downstream answer generation, chat persistence, and widget source cards continue
working without breaking changes.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Protocol

from app.schemas.contracts import HostContext, RetrievedEvidence

_TOKEN_RE = re.compile(r"[a-z0-9]{2,}")
_STOPWORDS = {
    "about",
    "after",
    "also",
    "and",
    "are",
    "can",
    "does",
    "for",
    "from",
    "have",
    "help",
    "how",
    "into",
    "more",
    "need",
    "please",
    "that",
    "the",
    "their",
    "there",
    "this",
    "what",
    "when",
    "where",
    "which",
    "with",
    "your",
}


class SearchableDocument(Protocol):
    """Minimal structural protocol so retrieval tests do not require ORM instances."""

    id: str
    tenant_id: str
    application_id: str
    module_id: str
    screen_id: str
    title: str
    original_filename: str
    source_uri: str
    source_type: str
    content: object | None


def tokenize_query(text: str) -> list[str]:
    """Lowercase alphanumeric tokenizer with simple stopword removal."""
    tokens = _TOKEN_RE.findall(text.lower())
    filtered = [tok for tok in tokens if tok not in _STOPWORDS]
    return filtered or tokens


class KnowledgeRetriever(ABC):
    """Independent retrieval interface decoupled from answer generation."""

    @abstractmethod
    def retrieve(
        self,
        *,
        query: str,
        documents: Sequence[SearchableDocument],
        context: HostContext,
        top_k: int = 3,
    ) -> list[RetrievedEvidence]:
        """Return ranked evidence items matching the query within tenant boundaries."""


class KeywordKnowledgeRetriever(KnowledgeRetriever):
    """Deterministic keyword-matching baseline retriever.

    Scores documents strictly within the caller's tenant using query term overlap
    across document title, filename, and extracted text segments.
    """

    def __init__(self, max_excerpt_chars: int = 360) -> None:
        self._max_excerpt_chars = max_excerpt_chars

    def retrieve(
        self,
        *,
        query: str,
        documents: Sequence[SearchableDocument],
        context: HostContext,
        top_k: int = 3,
    ) -> list[RetrievedEvidence]:
        query_terms = set(tokenize_query(query))
        if not query_terms:
            return []

        scored: list[RetrievedEvidence] = []
        for doc in documents:
            if doc.tenant_id != context.tenant_id:
                continue
            content_obj = getattr(doc, "content", None)
            extracted_text = getattr(content_obj, "extracted_text", "") if content_obj else ""
            if not extracted_text:
                continue

            segments_raw = getattr(content_obj, "segments_json", "[]") if content_obj else "[]"
            try:
                segments = json.loads(segments_raw) if isinstance(segments_raw, str) else []
            except json.JSONDecodeError:
                segments = []

            title_tokens = set(tokenize_query(f"{doc.title} {doc.original_filename}"))
            body_tokens = set(tokenize_query(extracted_text))
            matched_body = query_terms & body_tokens
            matched_title = query_terms & title_tokens
            matched_all = matched_body | matched_title

            if not matched_all:
                continue

            coverage = len(matched_all) / len(query_terms)
            title_bonus = 0.25 * (len(matched_title) / len(query_terms))
            context_bonus = 0.1 if doc.module_id == context.module_id else 0.0
            score = round(min(1.0, coverage + title_bonus + context_bonus), 4)

            best_excerpt, best_section, best_timestamp = self._select_best_excerpt(
                extracted_text=extracted_text,
                segments=segments,
                query_terms=query_terms,
            )

            scored.append(
                RetrievedEvidence(
                    document_id=doc.id,
                    file_name=doc.original_filename,
                    title=doc.title,
                    excerpt=best_excerpt,
                    relevance_score=score,
                    page_or_section=best_section,
                    timestamp_range=best_timestamp,
                    application_id=doc.application_id,
                    module_id=doc.module_id,
                    screen_id=doc.screen_id,
                    source_uri=doc.source_uri,
                    source_type=doc.source_type,
                )
            )

        scored.sort(key=lambda item: (-item.relevance_score, item.title.lower()))
        return scored[:top_k]

    def _select_best_excerpt(
        self,
        *,
        extracted_text: str,
        segments: list[dict[str, str | None]],
        query_terms: set[str],
    ) -> tuple[str, str | None, str | None]:
        best_text = extracted_text
        best_section: str | None = None
        best_timestamp: str | None = None
        best_hits = -1

        for seg in segments:
            seg_text = str(seg.get("text") or "").strip()
            if not seg_text:
                continue
            seg_tokens = set(tokenize_query(seg_text))
            hits = len(query_terms & seg_tokens)
            if hits > best_hits:
                best_hits = hits
                best_text = seg_text
                best_section = seg.get("page_or_section")
                best_timestamp = seg.get("timestamp_range")

        condensed = " ".join(best_text.split())
        if len(condensed) > self._max_excerpt_chars:
            condensed = condensed[: self._max_excerpt_chars - 1].rstrip() + "…"
        return condensed, best_section, best_timestamp
