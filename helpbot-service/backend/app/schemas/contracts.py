"""Pydantic API contracts and shared domain schemas for HelpBot.

These schemas intentionally expose clean extension seams for student assignments:
- `RetrievedEvidence` includes fields for relevance scores, page/section markers,
  timestamps, application/module/screen metadata, source URIs, and source types.
- `KnowledgeDocumentRead` keeps source metadata independent of extracted text.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HostContext(BaseModel):
    """Approved, minimal page and session context supplied by a host application.

    Host apps must NEVER include passwords, payment details, private form values,
    or raw page HTML in this object.
    """

    tenant_id: str = Field(default="campusdesk-dev", min_length=1, max_length=120)
    application_id: str = Field(default="campusdesk", min_length=1, max_length=120)
    user_id: str = Field(default="demo-student-001", min_length=1, max_length=120)
    role: str = Field(default="student", min_length=1, max_length=64)
    module_id: str = Field(default="general", min_length=1, max_length=120)
    screen_id: str = Field(default="home", min_length=1, max_length=120)
    route: str = Field(default="/", max_length=255)
    page_title: str = Field(default="", max_length=255)
    locale: str = Field(default="en-US", max_length=32)


class RetrievedEvidence(BaseModel):
    """Stable retrieval output schema shared by keyword and future semantic retrievers."""

    document_id: str
    file_name: str
    title: str
    excerpt: str
    relevance_score: float = Field(ge=0.0)
    page_or_section: str | None = None
    timestamp_range: str | None = None
    application_id: str
    module_id: str
    screen_id: str
    source_uri: str = ""
    source_type: str = "document"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: str | None = None
    context: HostContext = Field(default_factory=HostContext)


class ChatMessageRead(BaseModel):
    id: str
    sender: Literal["user", "assistant"]
    content: str
    sources: list[RetrievedEvidence] = Field(default_factory=list)
    created_at: datetime


class ChatResponse(BaseModel):
    conversation_id: str
    user_message: ChatMessageRead
    assistant_message: ChatMessageRead
    sources: list[RetrievedEvidence] = Field(default_factory=list)
    grounded: bool
    provider_used: str


class ConversationSummary(BaseModel):
    id: str
    tenant_id: str
    application_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationDetail(BaseModel):
    id: str
    tenant_id: str
    application_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageRead] = Field(default_factory=list)


class KnowledgeDocumentRead(BaseModel):
    id: str
    tenant_id: str
    application_id: str
    module_id: str
    screen_id: str
    title: str
    original_filename: str
    file_type: str
    source_type: str
    mime_type: str
    file_size_bytes: int
    character_count: int
    source_uri: str
    created_at: datetime


class DeleteResponse(BaseModel):
    deleted: bool
    id: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
    environment: str


class AIStatusResponse(BaseModel):
    provider: str
    model: str
    configured: bool
    ready: bool
    detail: str


class WidgetConfigResponse(BaseModel):
    api_base_url: str
    widget_script_url: str
    widget_title: str
    accent_color: str
    ai_ready: bool
    features: dict[str, bool]
    identity_mode: str
