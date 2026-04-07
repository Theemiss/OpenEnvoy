# AGENTS.md - Backend

**Purpose**: FastAPI REST API + AI processing engine

## STRUCTURE
```
backend/
├── api/v1/endpoints/    # REST routes
├── ai/clients/          # OpenAI, Anthropic, Ollama, OpenRouter
├── ai/scoring/          # Two-tier scoring
├── ai/classification/  # Reply classification
├── ai/resume_adaptation/
├── scrapers/sources/   # LinkedIn, Adzuna, Arbeitnow, Remotiv, RSS
├── engine/email/       # Gmail, SMTP, templates
├── engine/filters/      # Rule-based filtering
├── engine/tracking/    # Application history
├── engine/workflow/    # Celery + Temporal
├── models/             # SQLAlchemy models
├── schemas/            # Pydantic schemas
├── core/               # Config, DB, caching, logging
└── ingestion/          # Resume, GitHub, LinkedIn
```

## CONVENTIONS

- **Database**: SQLAlchemy 2.0 async, asyncpg driver
- **Models**: In `backend/models/`, use Base classes from core
- **Schemas**: Pydantic v2 in `backend/schemas/`
- **API Routes**: FastAPI in `backend/api/v1/endpoints/`
- **AI Clients**: Factory pattern in `backend/ai/clients/`

## TESTING

- Tests use pytest + pytest-asyncio
- `tests/conftest.py` provides fixtures with in-memory SQLite
- Run: `pytest -q` from repo root
- Fixtures: `event_loop`, `session`, sample data helpers

## ANTI-PATTERNS

- Never use `@ts-ignore` or `as any` (this is backend Python)
- Never suppress type errors with `# type: ignore`
- Never commit without running `./run_tests.sh`

## KEY FILES
| Task | Location |
|------|----------|
| API entry | `backend/main.py` |
| DB setup | `backend/core/database.py` |
| Config | `backend/core/config.py` |
| Celery tasks | `backend/engine/workflow/celery/tasks.py` |
