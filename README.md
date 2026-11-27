# HelpBot Training Suite

**HelpBot Training Suite** is a runnable reference monorepo designed for student developers and engineering interns. It demonstrates how to build an independently deployable, embeddable AI support assistant (**HelpBot Service**) and integrate it cleanly into an external host web application (**CampusDesk Student Services Portal**) across strict service boundaries.

## Repository Layout

```text
helpbot-training-suite/
├── campusdesk-demo/    # Fictional Vue 3 + Vite host portal (port 5173)
├── helpbot-service/    # Standalone FastAPI + SQLite + Shadow DOM widget (port 8200)
└── docs/               # Architecture, integration, API, privacy, and roadmap guides
```

## Service Boundaries

| Service | Default Local URL | Stack | Owns |
| --- | --- | --- | --- |
| **CampusDesk Demo Portal** | `http://127.0.0.1:5173` | Vue 3, Vite, JS, CSS | Host UI, demo user switcher, `window.HelpBotHostAdapter`, host loader |
| **HelpBot Service** | `http://127.0.0.1:8200` | Python 3.11+, FastAPI, SQLAlchemy, SQLite, `google-genai`, Shadow DOM Web Component | Knowledge ingestion, keyword retrieval baseline, AI provider, chat DB, widget assets |

- CampusDesk remains fully usable if HelpBot is stopped.
- HelpBot runs independently without CampusDesk and never imports host code or accesses host storage.

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** and **npm 9+**
- Optional: A **Google Gemini API key** for live LLM answers (HelpBot boots and passes all tests without one).

## Quick Start

### 1. Start HelpBot Service (Port 8200)

**Linux / macOS:**

```bash
cd helpbot-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Optional: set HELPBOT_GEMINI_API_KEY or set HELPBOT_AI_PROVIDER=mock in .env
python scripts/run_dev.py
```

**Windows PowerShell:**

```powershell
cd helpbot-service
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python scripts\run_dev.py
```

Verify health: open `http://127.0.0.1:8200/api/health` and `http://127.0.0.1:8200/api/ai/status`.

### 2. Seed Sample Knowledge (Optional, in a new terminal)

```bash
cd helpbot-service
python scripts/seed_sample_knowledge.py --base-url http://127.0.0.1:8200
```

### 3. Start CampusDesk Demo Portal (Port 5173)

**Linux / macOS:**

```bash
cd campusdesk-demo
npm install
cp .env.example .env.local
npm run dev
```

**Windows PowerShell:**

```powershell
cd campusdesk-demo
npm install
Copy-Item .env.example .env.local
npm run dev
```

Open `http://127.0.0.1:5173` in your browser. Switch pages and demo users to observe `window.HelpBotHostAdapter.getContext()` updating live.

## Running Tests

- **HelpBot backend (`pytest`, no API key required):**
  ```bash
  cd helpbot-service
  pytest
  ```
- **CampusDesk loader checks (Node built-in test runner):**
  ```bash
  cd campusdesk-demo
  npm test
  ```

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Local Development Guide](docs/local-development.md)
- [Host Integration Guide](docs/integration-guide.md)
- [API Reference](docs/api-reference.md)
- [Data & Privacy Guide](docs/data-and-privacy.md)
- [Student Contribution Guide](docs/student-contribution-guide.md)
- [Feature Roadmap (Student Assignments)](docs/feature-roadmap.md)
- [HelpBot Standalone Service README](helpbot-service/README.md)
