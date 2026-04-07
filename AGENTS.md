# PROJECT KNOWLEDGE BASE

**Generated:** 2026-04-06
**Commit:** c5dc5e6
**Branch:** main

## OVERVIEW

AI-Powered Job Application Automation System. Monorepo with FastAPI backend + Next.js frontend + Celery/Temporal workers.

## STRUCTURE
```
./
├── backend/          # FastAPI REST API + AI processing
├── frontend/         # Next.js 14+ (App Router)
├── workers/          # Celery workers (email, scoring, scraper)
├── tests/            # Pytest (unit + integration)
├── migrations/      # Alembic database migrations
├── docs/             # Development docs
└── infra/           # Infrastructure configs
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| API endpoints | backend/api/v1/endpoints/ | REST routes |
| AI clients | backend/ai/clients/ | OpenAI, Anthropic, Ollama, OpenRouter |
| Job scraping | backend/scrapers/sources/ | LinkedIn, Adzuna, Arbeitnow, Remotiv, RSS |
| Email engine | backend/engine/email/ | Gmail, SMTP, templates |
| Frontend pages | frontend/src/pages/ | Next.js App Router pages |
| Workers | workers/ | email_worker, scoring_worker, scraper_worker |

## CONVENTIONS

- **Backend**: FastAPI + SQLAlchemy 2.0 + Pydantic v2
- **DB**: PostgreSQL via asyncpg, Redis for caching
- **Async**: Celery + Temporal for workflows
- **Testing**: pytest + pytest-asyncio, factory-boy for fixtures
- **Formatting**: black, isort, ruff for linting
- **Frontend**: Next.js 14+ App Router, TypeScript, custom hooks in frontend/src/lib/hooks/

## ANTI-PATTERNS (THIS PROJECT)

- Do NOT use `@ts-ignore` or `as any` in TypeScript
- Do NOT suppress Python type errors
- NEVER commit without running tests first (see run_tests.sh)

## COMMANDS
```bash
# Backend
cd backend && uvicorn main:app --reload

# Frontend  
cd frontend && npm run dev

# Tests
./run_tests.sh

# Setup
./setup.sh
```

## NOTES

- Frontend has its own AGENTS.md (read FIRST for frontend work)
- Backend uses poetry for dependency management
- Workers require Redis + PostgreSQL to run
- Temporal workflow configs in backend/engine/workflow/temporal/
