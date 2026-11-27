"""Knowledge ingestion, validation, listing, and deletion service."""

from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.adapters.identity import AuthenticatedActor
from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.models.entities import KnowledgeDocument
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.contracts import KnowledgeDocumentRead
from app.security.file_safety import (
    generate_safe_storage_path,
    resolve_controlled_file_path,
    validate_upload_file,
)
from app.utilities.text_extractors import extract_document_text

logger = logging.getLogger("helpbot.services.knowledge")


class KnowledgeService:
    """Coordinates safe file ingestion, text extraction, and metadata persistence."""

    def __init__(self, session: Session, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._repo = KnowledgeRepository(session)

    def ingest_document(
        self,
        *,
        actor: AuthenticatedActor,
        raw_filename: str | None,
        content_type: str | None,
        content_bytes: bytes,
        application_id: str,
        module_id: str,
        screen_id: str,
        title: str | None = None,
        source_uri: str = "",
    ) -> KnowledgeDocumentRead:
        display_name, extension, mime_type, source_type = validate_upload_file(
            raw_filename=raw_filename,
            content_type=content_type,
            content_bytes=content_bytes,
            max_upload_bytes=self._settings.max_upload_bytes,
        )

        extraction = extract_document_text(extension, content_bytes)
        stored_filename, target_path = generate_safe_storage_path(
            self._settings.uploads_dir, extension
        )
        target_path.write_bytes(content_bytes)

        doc_title = (title or "").strip() or Path(display_name).stem.replace("_", " ").replace("-", " ")

        try:
            doc = self._repo.create_document(
                tenant_id=actor.tenant_id,
                application_id=application_id.strip() or "default",
                module_id=module_id.strip() or "general",
                screen_id=screen_id.strip() or "all",
                title=doc_title,
                original_filename=display_name,
                stored_filename=stored_filename,
                file_type=extension.lstrip("."),
                source_type=source_type,
                mime_type=mime_type,
                file_size_bytes=len(content_bytes),
                source_uri=source_uri.strip(),
                uploaded_by=actor.user_id,
                extracted_text=extraction.full_text,
                segments=extraction.segments_as_dicts(),
            )
            self._session.commit()
        except Exception:
            self._session.rollback()
            target_path.unlink(missing_ok=True)
            raise

        logger.info(
            "Ingested knowledge document id=%s type=%s size=%d chars=%d",
            doc.id,
            doc.file_type,
            doc.file_size_bytes,
            len(extraction.full_text),
        )
        return self._to_schema(doc)

    def list_documents(
        self,
        *,
        actor: AuthenticatedActor,
        application_id: str | None = None,
        module_id: str | None = None,
    ) -> list[KnowledgeDocumentRead]:
        docs = self._repo.list_documents(
            tenant_id=actor.tenant_id,
            application_id=application_id,
            module_id=module_id,
        )
        return [self._to_schema(doc) for doc in docs]

    def delete_document(self, *, actor: AuthenticatedActor, document_id: str) -> str:
        doc = self._repo.delete_document(document_id=document_id, tenant_id=actor.tenant_id)
        if doc is None:
            raise NotFoundError("Knowledge document not found.")
        self._session.commit()

        stored_path = resolve_controlled_file_path(
            self._settings.uploads_dir, doc.stored_filename
        )
        stored_path.unlink(missing_ok=True)
        logger.info("Deleted knowledge document id=%s", doc.id)
        return doc.id

    @staticmethod
    def _to_schema(doc: KnowledgeDocument) -> KnowledgeDocumentRead:
        char_count = doc.content.character_count if doc.content else 0
        return KnowledgeDocumentRead(
            id=doc.id,
            tenant_id=doc.tenant_id,
            application_id=doc.application_id,
            module_id=doc.module_id,
            screen_id=doc.screen_id,
            title=doc.title,
            original_filename=doc.original_filename,
            file_type=doc.file_type,
            source_type=doc.source_type,
            mime_type=doc.mime_type,
            file_size_bytes=doc.file_size_bytes,
            character_count=char_count,
            source_uri=doc.source_uri,
            created_at=doc.created_at,
        )
