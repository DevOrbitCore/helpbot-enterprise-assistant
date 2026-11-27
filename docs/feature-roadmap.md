# Feature Roadmap (Student Assignments)

The four advanced capabilities below are **not implemented in the baseline**. The baseline intentionally provides clean interfaces, database boundaries, and schemas so students can implement each assignment without rewriting core routes.

---

## Assignment 1: Context-Aware Semantic Knowledge Retrieval *(Not Implemented in Baseline)*

- **Goal**: Upgrade from document-level keyword matching to chunk-based semantic or hybrid retrieval with application/module/screen filtering, multi-document reasoning, and accurate chunk citations.
- **Extension Seams**:
  - `helpbot-service/backend/app/services/retrieval_service.py` — implement a new `KnowledgeRetriever` subclass (e.g., `HybridKnowledgeRetriever`).
  - `helpbot-service/backend/app/models/entities.py` — add a `KnowledgeChunk` table referencing `knowledge_documents.id`.
  - `helpbot-service/backend/app/schemas/contracts.py` — populate `relevance_score`, `page_or_section`, and `excerpt` on `RetrievedEvidence`.
- **Dependencies**: Local or API embedding provider behind a provider interface; keep offline mock embeddings for `pytest`.

## Assignment 2: Image & Screenshot Knowledge *(Not Implemented in Baseline)*

- **Goal**: Support PNG/JPEG uploads, vision-based UI/text extraction, provenance tracking, searchable extracted descriptions, and structured image references in chat answers.
- **Extension Seams**:
  - `helpbot-service/backend/app/security/file_safety.py` — extend `SUPPORTED_EXTENSIONS` and `EXTENSION_TO_SOURCE_TYPE` (`source_type="image"`).
  - `helpbot-service/backend/app/utilities/text_extractors.py` — add an image extraction adapter calling a vision provider interface.
  - `helpbot-service/backend/app/providers/base.py` — add an optional vision extraction interface so tests can mock it without API calls.

## Assignment 3: Video Tutorial Assistance *(Not Implemented in Baseline)*

- **Goal**: Register external or hosted tutorial videos, link uploaded `.vtt`/`.srt` transcripts to video records, discover relevant clips using host module/screen context, and display direct timestamped links in the widget.
- **Extension Seams**:
  - `helpbot-service/backend/app/utilities/text_extractors.py` — baseline `.vtt`/`.srt` extractors already preserve `timestamp_range` per segment.
  - `helpbot-service/backend/app/schemas/contracts.py` — `RetrievedEvidence` already includes `timestamp_range`, `source_uri`, and `source_type`.
  - `helpbot-service/widget/src/helpbot-widget.js` — render clickable video cards only once `features.video_tutorials` is enabled in `/api/widget-config`.

## Assignment 4: Voice Interaction *(Not Implemented in Baseline)*

- **Goal**: Add opt-in microphone input, speech-to-text, spoken AI answers, playback controls, and clear browser permission handling.
- **Extension Seams**:
  - `helpbot-service/backend/app/security/headers.py` — `Permissions-Policy` currently enforces `microphone=()`. Update this only behind an explicit, reviewed configuration flag.
  - `helpbot-service/backend/app/api/routes/system.py` — expose `features.voice_interaction: true` in `/api/widget-config` when enabled.
  - `helpbot-service/widget/src/helpbot-widget.js` — add accessible microphone and audio playback controls inside the Shadow DOM composer when the feature flag is active.
