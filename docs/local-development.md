# Local Development Guide

This guide covers setting up, running, and testing both services independently on Linux, macOS, and Windows PowerShell.

## 1. HelpBot Service (`http://127.0.0.1:8200`)

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

### Environment Variables (`helpbot-service/.env`)

- `HELPBOT_AI_PROVIDER`: `gemini` (default) or `mock` (offline deterministic mode).
- `HELPBOT_GEMINI_API_KEY`: Your Google Gemini API key (leave blank or placeholder to run without live AI calls).
- `HELPBOT_GEMINI_MODEL`: Defaults to `gemini-2.5-flash`.
- `HELPBOT_CORS_ORIGINS`: Comma-separated allowed host origins (`http://127.0.0.1:5173,http://localhost:5173`).
- `HELPBOT_MAX_UPLOAD_MB`: Upload size cap in MB (default `10`).

### Seed Sample Documents

With HelpBot running on port `8200`:

```bash
cd helpbot-service
python scripts/seed_sample_knowledge.py --base-url http://127.0.0.1:8200
```

## 2. CampusDesk Demo Portal (`http://127.0.0.1:5173`)

### Linux / macOS

```bash
cd campusdesk-demo
npm install
cp .env.example .env.local
npm run dev
```

### Windows PowerShell

```powershell
cd campusdesk-demo
npm install
Copy-Item .env.example .env.local
npm run dev
```

## 3. Verifying Offline Resilience

1. Stop the HelpBot Python process (`Ctrl+C`).
2. Reload `http://127.0.0.1:5173`.
3. Confirm CampusDesk still renders all six pages, switches demo users cleanly, and shows the non-blocking **HelpBot Offline (Portal Active)** status badge.

## 4. Running Automated Tests

```bash
# HelpBot backend tests (no API key or internet required)
cd helpbot-service
pytest -v

# CampusDesk host loader checks
cd campusdesk-demo
npm test
```
