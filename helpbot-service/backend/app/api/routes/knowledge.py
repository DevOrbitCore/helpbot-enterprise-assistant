"""Knowledge document upload, listing, and deletion routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.adapters.identity import AuthenticatedActor
from app.api.dependencies import (
    enforce_upload_rate_limit,
    get_current_actor,
    get_knowledge_service,
)
from app.schemas.contracts import DeleteResponse, KnowledgeDocumentRead
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.post(
    "/documents",
    response_model=KnowledgeDocumentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_upload_rate_limit)],
)
async def upload_knowledge_document(
    file: UploadFile = File(...),
    application_id: str = Form(default="campusdesk"),
    module_id: str = Form(default="general"),
    screen_id: str = Form(default="all"),
    title: str | None = Form(default=None),
    source_uri: str = Form(default=""),
    actor: AuthenticatedActor = Depends(get_current_actor),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> KnowledgeDocumentRead:
    content_bytes = await file.read()
    return knowledge_service.ingest_document(
        actor=actor,
        raw_filename=file.filename,
        content_type=file.content_type,
        content_bytes=content_bytes,
        application_id=application_id,
        module_id=module_id,
        screen_id=screen_id,
        title=title,
        source_uri=source_uri,
    )


@router.get("/documents", response_model=list[KnowledgeDocumentRead])
def list_knowledge_documents(
    application_id: str | None = Query(default=None),
    module_id: str | None = Query(default=None),
    actor: AuthenticatedActor = Depends(get_current_actor),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> list[KnowledgeDocumentRead]:
    return knowledge_service.list_documents(
        actor=actor,
        application_id=application_id,
        module_id=module_id,
    )


@router.delete("/documents/{document_id}", response_model=DeleteResponse)
def delete_knowledge_document(
    document_id: str,
    actor: AuthenticatedActor = Depends(get_current_actor),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> DeleteResponse:
    deleted_id = knowledge_service.delete_document(actor=actor, document_id=document_id)
    return DeleteResponse(deleted=True, id=deleted_id)
