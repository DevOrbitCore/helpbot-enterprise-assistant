# Architecture Overview

HelpBot Training Suite separates the **host application** (`campusdesk-demo`) from the **assistant service** (`helpbot-service`) at the process, storage, network, and UI layers.

## Service Boundaries

```text
+-----------------------------------+        HTTP + CORS Allowlist         +-----------------------------------+
|  CampusDesk Demo Portal (:5173)   |  <-------------------------------->  |     HelpBot Service (:8200)       |
|  - Vue 3 + Vite                   |   GET /api/widget-config             |  - FastAPI + SQLAlchemy + SQLite  |
|  - 6 Fictional Student Pages      |   GET /widget/src/helpbot-widget.js  |  - Knowledge Ingestion & Storage  |
|  - window.HelpBotHostAdapter      |   POST /api/chat                     |  - KeywordKnowledgeRetriever      |
|  - helpbot-loader.js              |   GET/DELETE /api/conversations      |  - AIProvider (Gemini / Mock)     |
|  - <helpbot-assistant> (ShadowDOM)|   POST/GET/DELETE /api/knowledge/*   |  - Shadow DOM Widget Assets       |
+-----------------------------------+                                      +-----------------------------------+
```

## Request & Integration Sequence

1. **Host Startup**: CampusDesk renders normally and registers `window.HelpBotHostAdapter.getContext()`.
2. **Non-Blocking Discovery**: `helpbot-loader.js` requests `GET http://127.0.0.1:8200/api/widget-config`. If HelpBot is offline, the loader returns `{ connected: false }` and CampusDesk continues functioning normally.
3. **Widget Mount**: When reachable, the loader dynamically injects `/widget/src/helpbot-widget.js`, mounts `<helpbot-assistant>`, and calls `element.configure(config, getContext)`.
4. **Context Synchronization**: Route changes or demo-user switches dispatch `helpbot:context-changed`. The widget refreshes its context pill and resets the active thread view so users never see another demo user's messages.
5. **Grounded Chat Flow**:
   - Widget sends `POST /api/chat` with the user's question, optional `conversation_id`, and approved `HostContext`.
   - `IdentityAdapter` resolves the server-side `(tenant_id, user_id, role)`.
   - `KnowledgeRetriever` retrieves matching evidence strictly inside `tenant_id`.
   - If zero evidence is found, `ChatService` returns `"I could not find this in the available HelpBot documents."` without calling the LLM.
   - If evidence is found, `AIProvider.generate_grounded_answer()` generates a response using only the retrieved excerpts and approved context.
   - Both messages and structured `RetrievedEvidence` items are persisted to SQLite under `(tenant_id, user_id)`.

## Storage Ownership

- **HelpBot Service** exclusively owns `helpbot-service/data/` (SQLite database, UUID-named uploaded files, and redacted logs).
- Static routes only expose `helpbot-service/widget/`. Runtime data directories, `.env`, and database files are never mounted or served.
- **CampusDesk Demo Portal** holds only in-memory fictional demo data and never reads or writes HelpBot storage.

## Key Extension Seams

- **Retrieval (`services/retrieval_service.py`)**: Swap or wrap `KeywordKnowledgeRetriever` via the `KnowledgeRetriever` ABC.
- **Knowledge Storage (`models/entities.py`)**: `KnowledgeDocument` (metadata) is decoupled from `KnowledgeContent` (extracted text + segments) so chunk and vector tables can attach to `knowledge_documents.id`.
- **AI Provider (`providers/base.py`)**: Swap `GeminiAIProvider` with any vendor implementing `AIProvider`.
- **Identity (`adapters/identity.py`)**: Replace `DevelopmentIdentityAdapter` with a production JWT/OIDC `IdentityAdapter`.
