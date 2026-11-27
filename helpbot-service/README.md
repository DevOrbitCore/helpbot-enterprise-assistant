# HelpBot Standalone Service

HelpBot is an independently runnable support assistant service consisting of:

1. **FastAPI Backend (`backend/app/`)**: Knowledge document ingestion, deterministic keyword retrieval baseline, provider-agnostic AI answering (`google-genai` Gemini SDK + offline `MockAIProvider`), and tenant/user-isolated SQLite conversation persistence.
2. **Embeddable Shadow DOM Widget (`widget/`)**: Browser-native `<helpbot-assistant>` Web Component served at `/widget/src/helpbot-widget.js`.

HelpBot has zero dependency on CampusDesk and can be embedded into any web application.

## Setup & Running Standalone

### Linux / macOS

```bash
cd helpbot-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/run_dev.py
```

### Windows PowerShell

```powershell
cd helpbot-service
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python scripts\run_dev.py
```

The service listens on `http://127.0.0.1:8200` by default.

## Running Without a Gemini API Key

- Leave `HELPBOT_GEMINI_API_KEY` as the placeholder to verify graceful unconfigured startup (`GET /api/ai/status` returns `"ready": false`).
- Or set `HELPBOT_AI_PROVIDER=mock` in `.env` to test grounded retrieval and chat persistence offline using `MockAIProvider`.

## Supported Baseline Document Formats

- `.pdf`, `.docx`, `.md`, `.html`/`.htm`, `.txt`, `.vtt`, `.srt`
- Image ingestion (PNG/JPEG), semantic/vector search, video tutorial playback cards, and voice interaction are **not implemented in the baseline** and are reserved for student assignments (see `../docs/feature-roadmap.md`).

## Running Automated Tests

```bash
cd helpbot-service
pytest -v
```
