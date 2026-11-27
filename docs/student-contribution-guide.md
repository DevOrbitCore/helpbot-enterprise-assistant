# Student Contribution Guide

Welcome to the HelpBot Training Suite! Follow this workflow when implementing assigned features.

## Branch Naming

Create a focused branch from `main` using your assignment slug:

- `feat/semantic-retrieval`
- `feat/image-knowledge`
- `feat/video-tutorials`
- `feat/voice-interaction`
- `fix/<short-issue-description>`

## Issue Workflow

1. Read `docs/feature-roadmap.md` and `docs/architecture.md` before modifying code.
2. Keep strict service boundaries: do **not** import CampusDesk files from `helpbot-service` or bypass the HTTP/adapter contract.
3. Preserve backward compatibility with existing baseline endpoints and `RetrievedEvidence` fields.
4. Never commit `.env`, API keys, SQLite databases, uploaded files, or generated embeddings.

## Testing Expectations

- Every backend change must include `pytest` unit/integration tests that pass **without** network calls or a Gemini API key (use `MockAIProvider` or local mocks).
- Frontend or widget changes must keep `campusdesk-demo` working cleanly when HelpBot is offline and include updated checks in `campusdesk-demo/tests/`.
- Run `ruff check backend tests` (if installed) and `pytest -v` before opening a pull request.

## Pull Request Checklist

- [ ] Linked to the assigned GitHub issue and explains the architectural approach.
- [ ] All baseline and newly added automated tests pass offline (`pytest` and `npm test`).
- [ ] Security boundaries preserved (tenant/user isolation, CORS, upload validation, no secrets logged).
- [ ] Includes screenshots or short demo evidence (terminal output or UI recording) showing the feature working locally.
- [ ] Updated relevant documentation in `docs/` (`api-reference.md`, `data-and-privacy.md`, `feature-roadmap.md`).
