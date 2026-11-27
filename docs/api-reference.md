# HelpBot API Reference

Base URL (local default): `http://127.0.0.1:8200`

## Development Identity Headers

In local development mode (`HELPBOT_ALLOW_DEV_IDENTITY=true`), user- and tenant-scoped endpoints accept:

- `X-HelpBot-Tenant-Id` (default: `campusdesk-dev`)
- `X-HelpBot-User-Id` (default: `demo-student-001`)
- `X-HelpBot-User-Role` (default: `student`)

---

## System Endpoints

### `GET /api/health`
Returns service liveness metadata.

```json
{
  "status": "ok",
  "service": "helpbot-service",
  "version": "0.1.0",
  "environment": "development"
}
```

### `GET /api/ai/status`
Reports whether the configured AI provider is ready without exposing secrets.

```json
{
  "provider": "gemini",
  "model": "gemini-2.5-flash",
  "configured": false,
  "ready": false,
  "detail": "HELPBOT_GEMINI_API_KEY is not configured. Set a valid Gemini API key in helpbot-service/.env to enable live AI responses."
}
```

### `GET /api/widget-config`
Returns non-sensitive configuration used by host loaders to mount `<helpbot-assistant>`.

```json
{
  "api_base_url": "http://127.0.0.1:8200",
  "widget_script_url": "http://127.0.0.1:8200/widget/src/helpbot-widget.js",
  "widget_title": "HelpBot Support Assistant",
  "accent_color": "#1d4ed8",
  "ai_ready": false,
  "features": {
    "semantic_retrieval": false,
    "image_knowledge": false,
    "video_tutorials": false,
    "voice_interaction": false
  },
  "identity_mode": "development-only"
}
```

---

## Chat & Conversation Endpoints

### `POST /api/chat`
Sends a question, retrieves tenant-scoped evidence, generates a grounded answer (or returns the no-evidence guard message), and persists the turn.

**Request:**
```json
{
  "message": "How many days is the undergraduate library loan period?",
  "conversation_id": null,
  "context": {
    "tenant_id": "campusdesk-dev",
    "application_id": "campusdesk",
    "user_id": "stu-maya-chen",
    "role": "student",
    "module_id": "library-services",
    "screen_id": "borrowing-rules",
    "route": "/library",
    "page_title": "Library Services",
    "locale": "en-US"
  }
}
```

**Response (`200 OK`):** Returns `conversation_id`, `user_message`, `assistant_message`, `sources` (array of `RetrievedEvidence`), `grounded`, and `provider_used`.

### `GET /api/conversations`
Lists conversations belonging strictly to the authenticated `(tenant_id, user_id)`.

### `GET /api/conversations/{conversation_id}`
Returns full message history for a conversation owned by the caller. Returns `404` if the ID belongs to another user or tenant.

### `DELETE /api/conversations/{conversation_id}`
Deletes a conversation owned by the caller. Returns `404` if owned by another user or tenant.

---

## Knowledge Document Endpoints

### `POST /api/knowledge/documents` (`multipart/form-data`)
Uploads and extracts text from `.pdf`, `.docx`, `.md`, `.html`/`.htm`, `.txt`, `.vtt`, or `.srt`.

Form fields: `file` (required), `application_id`, `module_id`, `screen_id`, `title`, `source_uri`.

### `GET /api/knowledge/documents`
Lists uploaded documents for the caller's tenant. Optional query filters: `application_id`, `module_id`.

### `DELETE /api/knowledge/documents/{document_id}`
Deletes the metadata, extracted content, and stored file for a document in the caller's tenant.
