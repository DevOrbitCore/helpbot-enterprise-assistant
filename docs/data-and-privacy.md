# Data, Security, and Privacy Guide

## What Is Stored Locally and Where

All HelpBot runtime state is stored strictly inside `helpbot-service/data/` (git-ignored):

| Path | Contents |
| --- | --- |
| `helpbot-service/data/helpbot.db` | SQLite database containing `conversations`, `chat_messages`, `knowledge_documents`, and `knowledge_contents`. |
| `helpbot-service/data/uploads/` | Uploaded knowledge files saved under UUID-generated filenames (original client paths are never used on disk). |
| `helpbot-service/data/logs/helpbot.log` | Operational logs filtered by `RedactingFilter` (API keys, bearer tokens, document bodies, and raw user prompts are not logged). |

None of these directories are exposed over HTTP static routes.

## What Is Sent to the AI Provider (Privacy Notice)

When `HELPBOT_AI_PROVIDER=gemini` and a valid `HELPBOT_GEMINI_API_KEY` is configured, HelpBot sends an outbound request to Google Gemini **only** when:

1. A user submits a message to `POST /api/chat`, **and**
2. Baseline retrieval finds at least one matching evidence excerpt in the tenant's knowledge base.

Each Gemini request includes:
- The user's chat question
- The minimal approved `HostContext` (`application_id`, `module_id`, `screen_id`, `locale`)
- The top retrieved documentation excerpts

HelpBot **never** sends the host page's full DOM, passwords, payment details, or unrelated tenant documents to Gemini. When `HELPBOT_AI_PROVIDER=mock` or no evidence is retrieved, zero outbound AI calls are made.

## Security Defaults

- **CORS Allowlist**: Only origins explicitly listed in `HELPBOT_CORS_ORIGINS` are permitted.
- **Permissions-Policy**: `microphone=(), camera=(), geolocation=()` is sent on every response. Microphone access is disabled by default and must not be enabled until the voice assignment completes a security review.
- **Rate Limiting**: Local development uses `InMemoryRateLimiter` on `POST /api/chat` and `POST /api/knowledge/documents`. Replace with Redis or an API gateway in production.
- **Tenant & User Isolation**: All conversation queries filter on `(tenant_id, user_id)` resolved by `IdentityAdapter`.

## Clearing Local Data

Stop the HelpBot server, then remove local runtime files:

**Linux / macOS:**
```bash
rm -f helpbot-service/data/helpbot.db helpbot-service/data/logs/*.log
find helpbot-service/data/uploads -type f ! -name '.gitkeep' -delete
```

**Windows PowerShell:**
```powershell
Remove-Item -Force -ErrorAction SilentlyContinue helpbot-service\data\helpbot.db, helpbot-service\data\logs\*.log
Get-ChildItem helpbot-service\data\uploads -File | Where-Object { $_.Name -ne '.gitkeep' } | Remove-Item -Force
```
