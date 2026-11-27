"""Tenant-scoped SQLAlchemy repository for knowledge documents and extracted content."""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import KnowledgeContent, KnowledgeDocument


class KnowledgeRepository:
    """Stores document metadata separately from extracted text content."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_document(
        self,
        *,
        tenant_id: str,
        application_id: str,
        module_id: str,
        screen_id: str,
        title: str,
        original_filename: str,
        stored_filename: str,
        file_type: str,
        source_type: str,
        mime_type: str,
        file_size_bytes: int,
        source_uri: str,
        uploaded_by: str,
        extracted_text: str,
        segments: list[dict[str, str | None]],
    ) -> KnowledgeDocument:
        doc = KnowledgeDocument(
            tenant_id=tenant_id,
            application_id=application_id,
            module_id=module_id,
            screen_id=screen_id,
            title=title[:255],
            original_filename=original_filename[:255],
            stored_filename=stored_filename,
            file_type=file_type,
            source_type=source_type,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            source_uri=source_uri[:500],
            uploaded_by=uploaded_by[:120],
        )
        doc.content = KnowledgeContent(
            extracted_text=extracted_text,
            segments_json=json.dumps(segments),
            character_count=len(extracted_text),
        )
        self._session.add(doc)
        self._session.flush()
        return doc

    def list_documents(
        self,
        tenant_id: str,
        application_id: str | None = None,
        module_id: str | None = None,
    ) -> list[KnowledgeDocument]:
        stmt = (
            select(KnowledgeDocument)
            .options(selectinload(KnowledgeDocument.content))
            .where(KnowledgeDocument.tenant_id == tenant_id)
            .order_by(KnowledgeDocument.created_at.desc())
        )
        if application_id:
            stmt = stmt.where(KnowledgeDocument.application_id == application_id)
        if module_id:
            stmt = stmt.where(KnowledgeDocument.module_id == module_id)
        return list(self._session.scalars(stmt).all())

    def get_document(self, document_id: str, tenant_id: str) -> KnowledgeDocument | None:
        stmt = (
            select(KnowledgeDocument)
            .options(selectinload(KnowledgeDocument.content))
            .where(
                KnowledgeDocument.id == document_id,
                KnowledgeDocument.tenant_id == tenant_id,
            )
        )
        return self._session.scalars(stmt).first()

    def delete_document(self, document_id: str, tenant_id: str) -> KnowledgeDocument | None:
        doc = self.get_document(document_id, tenant_id)
        if doc is None:
            return None
        self._session.delete(doc)
        self._session.flush()
        return doc
