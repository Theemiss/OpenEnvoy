# AI-Powered Job Application Automation System
### Architecture, Design & Implementation Guide

| | |
|---|---|
| **Version** | 1.0 — Initial Release |
| **Audience** | Engineering & Product Teams |
| **Classification** | Internal / Confidential |
| **Status** | Architecture Planning |

---

## Executive Summary

This document defines the architecture for a cost-efficient, AI-augmented job application automation system. The system is designed around a foundational principle: use code wherever possible, and invoke AI strictly where genuine reasoning is required.

Most job-hunting automation tools fail for one of two reasons: they over-rely on AI for tasks that deterministic code can handle better and cheaper, or they attempt to be fully autonomous agents that introduce unpredictable behavior. This system avoids both traps.

> **Core Design Principle:** AI is a specialized tool in this system — not the operating system. Deterministic pipelines do the heavy lifting. AI handles scoring, writing, and classification — nothing more.

The system is composed of four primary layers:

- **Data Layer** — the structured knowledge base about you, your experience, and your job history
- **Ingestion Pipelines** — automated code-only parsers for GitHub, LinkedIn, and resumes
- **Job Collection Engine** — scrapers and aggregators that continuously gather job opportunities
- **AI Execution Layer** — a tightly controlled set of AI tasks: scoring, CV adaptation, email drafting, and reply classification

When operating at scale (e.g. 100 jobs scraped), approximately 80% of work is handled entirely by rules and code, with AI invoked only for the final 20% of shortlisted opportunities. This keeps costs minimal while maintaining quality output.

---

## 1. Core Architecture (Cost-Efficient by Design)

The fundamental design choice of this system is to use AI only where human-like reasoning is genuinely required. Every other operation — data extraction, filtering, scheduling, storing — is implemented as deterministic code. This is not a limitation; it is the correct engineering decision.

### 1A. Data Layer — The Career Brain

All career-related information is centralized into a single structured store. This acts as the system's long-term memory, allowing every downstream component to draw from a single source of truth.

**Data entities managed:**

- **Resume** — multiple versions, with metadata on which version was sent where
- **Projects** — parsed and structured from GitHub repositories
- **Experience & Skills** — canonical structured representation of your professional history
- **Job Application History** — every application made, with status and outcome
- **Recruiter Conversations** — indexed and searchable communication log
- **Linked Profiles** — data imported from LinkedIn and other platforms

**Recommended storage stack:**

| Component | Technology | Purpose |
|---|---|---|
| Primary Database | PostgreSQL | All structured data: jobs, profiles, applications, history |
| Object Storage | AWS S3 / Cloudflare R2 | CV versions (PDF/DOCX), attachments, raw scrape dumps |
| Vector Database | Qdrant / Weaviate *(optional)* | Semantic search over job descriptions and profiles |
| Cache Layer | Redis | Short-lived data: job queue, deduplication keys, rate limits |

> **Note:** The vector database is optional. Only add it if you implement semantic job matching. Do not over-engineer the initial stack.

---

### 1B. Ingestion Pipelines — Mostly Code, No AI

Data enters the system through three primary ingestion channels. All three are implemented as code-only pipelines — no AI calls at this stage.

#### GitHub Sync

Connects to the GitHub API to extract a structured view of your development work. This data feeds directly into resume generation and job matching.

- **Repositories** — name, description, visibility, language composition, star count
- **Languages** — aggregated usage statistics across all public repositories
- **README Summaries** — extracted via text parsing (not AI), stored as project descriptions
- **Commit Activity** — frequency and recency, used as a proxy for engagement and skill currency

> No AI is required here. Repositories are parsed, tagged, and stored deterministically. AI can optionally enrich descriptions later, but it is not part of the ingestion step.

#### LinkedIn Import

LinkedIn's API access is highly restricted for third-party applications. Practical approaches are:

- **Manual Export** — LinkedIn provides a GDPR data export (CSV + JSON) that can be parsed on a scheduled basis
- **Controlled Scraping** — using Playwright with authenticated cookies; requires careful rate limiting and ethical use

> ⚠️ **Risk:** LinkedIn actively detects and restricts automated access. Use rate limiting, human-like delays, and do not run scrapers from production IP ranges. Respect platform terms of service.

#### Resume Parser

The canonical resume is parsed once into a structured JSON representation. This becomes the base template that all AI-generated tailored versions derive from.

- Input: DOCX or PDF resume
- Output: structured JSON — sections, skills list, experience objects, dates
- Storage: canonical version in PostgreSQL; raw file in object storage
- Strategy: store all generated versions to avoid regenerating the same output twice

---

## 2. Job Collection Engine

The job collection engine is a continuously running data pipeline that discovers, normalizes, and stores job postings from multiple sources. This is entirely code-driven — no AI is involved at the collection stage.

### 2A. Data Sources

- Job board APIs — where available (e.g. LinkedIn Jobs API, Adzuna, Remotive, Arbeitnow for European markets)
- Web scraping — Playwright-based scrapers for boards that don't offer public APIs
- RSS feeds — many niche job boards publish jobs via RSS, which is trivially parseable
- Email digests — optionally parse job alert emails via IMAP

### 2B. Collection Pipeline

The pipeline runs on a cron schedule and follows a strict sequence:

1. **Trigger** — cron job fires on schedule (e.g. every 4–6 hours)
2. **Scrape** — Playwright fetches job listings from configured sources
3. **Normalize** — raw HTML/JSON is parsed into a canonical job schema
4. **Deduplicate** — hash-based check against existing records; duplicates are discarded
5. **Store** — new jobs written to PostgreSQL with metadata (source, timestamp, URL)
6. **Queue** — new job IDs pushed into Redis queue for downstream processing

| Parameter | Value |
|---|---|
| Cron Schedule | Every 4–6 hours (configurable per source) |
| Deduplication | URL hash + title + company hash; checked against existing records |
| Normalization | Title, company, location, salary range, description, required skills |
| Retention Policy | Jobs older than 90 days marked stale; purged at 180 days |
| Error Handling | Failed scrapes logged; exponential backoff retry; alert after 3 failures |

---

## 3. Where AI Should Be Used (Strictly Limited)

> **This is where most implementations go wrong.** AI is expensive, slow, and non-deterministic. It should be used only where its reasoning capability produces value that code cannot replicate.

There are exactly **four AI tasks** in this system. Each has a defined input, output, and escalation rule. Everything else is code.

### 3A. Job Relevance Scoring

Before investing time in CV adaptation or email drafting, every job is scored for relevance. This is the system's primary AI gate.

| Parameter | Detail |
|---|---|
| Input | Job description text + canonical profile JSON |
| Output | Match score (0–100) + short reasoning paragraph |
| Model Strategy | Run cheap/fast model first (e.g. GPT-4o-mini, Haiku); escalate to stronger model only if score is ambiguous (40–60 range) |
| Threshold | Score >= 70 proceeds to CV adaptation; below threshold is archived |
| Caching | Identical job descriptions return cached score; never re-score same job |

The two-tier model approach is critical for cost control. The vast majority of jobs are either clearly relevant or clearly not, and a cheap model handles these correctly. Only genuinely ambiguous cases require a more capable model.

### 3B. Resume Adaptation (Critical Path)

For each shortlisted job, the system generates a tailored version of the canonical resume. This is the highest-value AI task in the entire pipeline.

The AI is instructed to modify:

- **Professional Summary** — rewritten to mirror the job's language and priorities
- **Skills Emphasis** — relevant skills promoted; less relevant skills de-emphasized or omitted
- **Project Ordering** — most relevant projects listed first
- **Experience Framing** — accomplishment bullets reworded to match the role's requirements

> **Important:** Every generated CV version is stored with a reference to the job ID it was created for. If the same job is re-queued, the existing CV is retrieved from storage — never regenerated. This deduplication strategy is the single most effective cost optimization in the system.

### 3C. Cover Letter and Email Personalization

Short, targeted emails are generated per application. These are not generic templates — they reference specific details from the job description and the company.

- Target length: 150–250 words for initial outreach
- AI prompt includes: job description, company name, relevant projects, tone instructions
- Output is stored alongside the application record
- Human review is recommended before sending (see Section 5)

### 3D. Recruiter Reply Classification and Response Drafting

Incoming recruiter emails are classified into one of four categories, then handled accordingly.

| Category | Action | Automation Level |
|---|---|---|
| Interview Invitation | Draft acceptance/scheduling reply; notify user for approval | Semi-automated |
| Rejection | Log outcome against application; update job status | Fully automated |
| Request for Information | Draft informational reply; attach relevant CV version | Semi-automated |
| Ambiguous / Other | Flag for manual review; no automated action | Manual |

---

## 4. Automation Engine

The automation engine is the operational backbone of the system. It orchestrates all the components — ingestion, scoring, CV generation, email sending, and follow-up — into a coherent, reliable workflow. This layer contains no AI.

### 4A. Workflow Engine

Temporal is the recommended workflow orchestration framework. It provides durable execution, automatic retries, and a full activity history — critical for a system that may run for months.

**Alternative options by complexity:**

| Option | Notes |
|---|---|
| Temporal | Best choice. Durable workflows, retry logic, versioning, full observability |
| Celery + Redis | Simpler setup, sufficient for MVP; less durable under failures |
| Airflow | Good for batch-heavy pipelines; overhead is high for event-driven flows |
| Simple Queue (RQ) | Minimum viable option; no durability guarantees |

**Core workflow for each new job discovered:**

1. New job written to database and pushed to processing queue
2. Rule-based filter applied (location, seniority, salary, keywords) — no AI
3. If passes filter: AI scoring invoked
4. If score >= threshold: CV adaptation queued
5. Tailored CV generated and stored
6. Personalized email drafted
7. Email sent (or queued for human approval, depending on configuration)
8. Application logged with all metadata
9. Follow-up timer set (default: 5 business days)

### 4B. Email System

All outbound email is managed through either the Gmail API (OAuth) or direct SMTP. The system maintains a complete log of all email activity.

- **Sent emails** — logged with timestamp, recipient, job ID, CV version ID
- **Replies** — monitored via IMAP polling or Gmail push notifications
- **Follow-ups** — automatically scheduled; cancelled if a reply is received
- **Spam protection** — rate limiting, natural send delays, domain warm-up for new addresses

> ⚠️ **Email deliverability is one of the hardest operational challenges.** Sending too fast, from a cold domain, or with templated content will result in spam classification. Rate limit aggressively and vary email content.

### 4C. Application History Tracking

Every action taken by the system is logged. This history serves three purposes: auditability, debugging, and future model improvement.

- Job discovered — source, timestamp, normalized job data
- Rule filter outcome — pass/fail with reason code
- AI score — score value, model used, reasoning excerpt
- CV version — ID of generated CV, diff from canonical version
- Email sent — timestamp, content hash, recipient
- Recruiter response — classification, response content, timestamp
- Final outcome — hired, rejected, ghosted, withdrawn

This dataset becomes the foundation for a feedback loop in later system iterations (see Section 8).

---

## 5. Semi-Agent Behavior (Controlled Autonomy)

> **This system is deliberately NOT a fully autonomous agent.** Full autonomy introduces compounding errors, unpredictable behavior, and reputational risk. The correct model is controlled, deterministic automation with AI as a constrained specialist.

### 5A. The Correct Model

The system operates as a controlled pipeline where AI plays a bounded, well-defined role at each stage. Think of AI as a highly capable contractor with a specific job description — not as an executive making decisions.

| Role | Task |
|---|---|
| AI Role: Evaluator | Score job relevance against profile |
| AI Role: Writer | Generate tailored CV sections and email drafts |
| AI Role: Classifier | Categorize incoming recruiter replies |
| NOT AI's Role | Deciding whether to apply to a job autonomously |
| NOT AI's Role | Sending emails without human review of high-stakes messages |
| NOT AI's Role | Modifying application strategy based on outcomes (until feedback loop is built) |

### 5B. Human-in-the-Loop Gates

The following actions require explicit human approval before the system proceeds:

- Accepting an interview invitation — the system drafts the reply, the user reviews and confirms
- Applying to a senior or executive role — additional review gate triggered by seniority detection
- Sending a follow-up to a recruiter who has previously replied — requires manual decision
- Any application where the AI score is in the ambiguous range (40–70) — user prompted to decide

For all other actions (filtering, scoring, archiving, standard follow-ups), the system operates automatically without interruption.

---

## 6. Cost Optimization Strategy

Cost control is a first-class architectural concern, not an afterthought. The following strategies are implemented at the design level to minimize AI spend without sacrificing output quality.

### 6A. Optimization Rules

- **Cache everything** — every AI output is stored against a deterministic key derived from its inputs
- **Never regenerate** — if a CV was created for a job, retrieve it; never call the AI again for the same job
- **Cheap models first** — use the smallest model that can handle the task; escalate only when necessary
- **Batch where possible** — group scoring requests into batches to reduce API overhead
- **Rules before AI** — eliminate obviously irrelevant jobs with code before any AI call is made
- **Embedding-based deduplication** — use embeddings to detect near-duplicate job postings before scoring

### 6B. Example Cost Flow at Scale

| Pipeline Stage | Jobs | AI Involved | Notes |
|---|---|---|---|
| Scraped | 100 | No | Raw collection; code-only pipeline |
| Rule-filtered out | 80 | No | Location, seniority, salary, keyword filters |
| AI-scored | 20 | Yes (cheap model) | Only shortlisted candidates reach this stage |
| Score ambiguous — escalated | 3 | Yes (premium model) | Edge cases only |
| CV adaptations generated | 5 | Yes | High-score shortlist; cached permanently |
| Emails drafted | 5 | Yes | Short, targeted; stored against application record |
| Follow-ups | 2 | No | Template-based; triggered by timer logic |

At this ratio — 80% filtered by code, 20% evaluated by AI, 5% receiving full CV and email treatment — monthly AI costs remain well under $10 for typical job search volumes.

### 6C. Caching Architecture

| Key Type | Strategy |
|---|---|
| CV Cache Key | `SHA256(canonical_profile_hash + job_description_hash)` |
| Score Cache Key | `SHA256(job_id + profile_version_id)` |
| Email Cache Key | `SHA256(job_id + profile_version_id + template_id)` |
| Cache Backend | Redis (TTL: 30 days for scores; permanent for CVs) |
| Cache Miss Strategy | Generate, store, then return; never generate twice |

---

## 7. Technology Stack

### 7A. Full Stack Reference

| Layer | Technology | Justification |
|---|---|---|
| API Backend | Python / FastAPI | Async-first, type-safe, excellent OpenAPI support |
| Primary Database | PostgreSQL | Proven, relational, excellent JSON support via JSONB |
| Cache / Queue | Redis | Sub-millisecond latency; used for queues, deduplication, and caching |
| Object Storage | AWS S3 / Cloudflare R2 | Cost-effective binary storage for CVs and attachments |
| Web Scraping | Playwright (Python) | Handles JavaScript-rendered pages; supports authenticated sessions |
| Workflow Engine | Temporal | Durable execution, automatic retries, versioned workflows |
| Task Queue (alt) | Celery + Redis | Simpler MVP option if Temporal is too complex initially |
| AI — Cloud | OpenAI / Anthropic API | Flexible; swap models per task based on cost/capability tradeoff |
| AI — Local | Ollama + Llama 3 / Mistral | For scoring and classification tasks; zero cost per call |
| Embeddings | OpenAI text-embedding-3-small | Low cost; used for deduplication and semantic search |
| Email | Gmail API / SMTP (SendGrid) | Gmail API for personal use; SendGrid for volume sending |
| Frontend *(optional)* | Next.js | Dashboard for review queues, application history, metrics |

### 7B. Infrastructure Notes

- Run all background workers (scrapers, queue processors) on a small VPS or AWS EC2 t3.small — not Lambda, as jobs can run for minutes
- Use Docker Compose for local development; Kubernetes only if scaling beyond a single team
- Secrets management via environment variables minimum; AWS Secrets Manager or Doppler for production
- Monitoring: Sentry for error tracking; Prometheus + Grafana for queue depth and API call rates

---

## 8. Legal and Platform Risk Management

> ⚠️ **Platform risk is real and must be managed deliberately.** Ignoring it is not a viable strategy — it will result in account bans, email blocks, or legal exposure.

### 8A. Risk Summary

| Risk | Severity | Mitigation |
|---|---|---|
| LinkedIn scraping | High | Rate limiting, human-like delays, cookie rotation, export fallback |
| Email spam classification | High | Domain warm-up, volume limits, personalized content, SPF/DKIM/DMARC |
| Job board ToS violations | Medium | Read ToS per board; prefer official APIs; disclose automation where required |
| AI-generated content detection | Low–Medium | Ensure outputs are genuinely tailored, not templated |
| Data privacy (GDPR) | Medium | Store only data you own; provide data deletion capability |

### 8B. Operational Safeguards

- **Rate limiting** — all scrapers implement per-domain rate limits with exponential backoff on errors
- **Human-in-the-loop** — all high-stakes actions require manual approval
- **Multiple sending identities** — use separate email addresses for different geographic markets if sending at volume
- **Activity logging** — every automated action is logged with timestamp, enabling audit and rollback
- **Kill switch** — a single configuration flag must be able to halt all automated sending immediately

---

## 9. Feedback Loop and System Evolution

Once the base system is operating reliably, the application history data accumulated over weeks of use enables a significant upgrade: a feedback loop that improves the system's decision-making over time.

### 9A. Feedback Signal Collection

The system already stores all the data needed for feedback analysis:

- Which CV versions received recruiter responses
- Which email styles produced replies vs. were ignored
- Which job types correlated with interview invitations
- Which companies responded to follow-ups

After 4–8 weeks of operation, this dataset becomes statistically meaningful.

### 9B. Reinforcement Mechanisms

- **CV Strategy Optimization** — identify which sections or phrasings in tailored CVs correlate with responses; weight these higher in future generations
- **Email Template Evolution** — A/B test email styles by varying tone, length, and opening line; track response rates
- **Job Prioritization Tuning** — refine the scoring model's weighting based on which job types actually led to conversations
- **Recruiter Pattern Recognition** — identify recruiters who consistently respond and prioritize similar outreach

> This feedback mechanism transforms the system from a static automation tool into a progressively improving job search engine. The longer it runs, the better its recommendations become.

---

## 10. Implementation Roadmap

This is not a weekend project. Approaching it as one is the most common reason similar systems fail. The following timeline assumes a single developer working part-time alongside other commitments.

> **Reality Check:** A production-grade version is 2–4 weeks for a working MVP, and 2–3 months for a reliable, maintainable system.

### Phase 1 — Foundation (Weeks 1–2)

1. Database schema — design and migrate PostgreSQL tables for jobs, applications, CVs, emails
2. GitHub ingestion pipeline — connect API, parse repos, store structured data
3. Resume parser — convert canonical CV to structured JSON
4. Job scraper — one source (e.g. LinkedIn or Adzuna) working end-to-end
5. Manual review UI — basic table view of scraped jobs in a Next.js dashboard

### Phase 2 — AI Integration (Weeks 3–4)

1. Rule-based filter — implement keyword, location, and seniority filters
2. AI scoring — integrate cheap model for relevance scoring; test on sample jobs
3. CV adaptation — implement tailored CV generation; store outputs
4. Email drafting — generate and store outreach emails; no sending yet
5. Cost tracking — log every AI API call with model, tokens, and cost estimate

### Phase 3 — Automation (Weeks 5–8)

1. Temporal workflow — replace manual triggers with durable automated pipeline
2. Email sending — integrate Gmail API; implement rate limiting and logging
3. Reply monitoring — IMAP polling; classify replies; update application status
4. Follow-up logic — automatic follow-up scheduling and cancellation
5. Human approval queue — dashboard for reviewing AI-drafted responses

### Phase 4 — Hardening (Month 3)

1. Multi-source scraping — add 3–5 job sources; normalize to canonical schema
2. Feedback loop v1 — basic analytics on response rates per CV version and email style
3. Error handling and alerting — Sentry integration; email alerts on scraper failures
4. LinkedIn export parser — process manual data exports into the system
5. Documentation and runbook — operational guide for maintaining the system

| Parameter | Value |
|---|---|
| MVP Timeline | 2–4 weeks (single developer, part-time) |
| Production System | 2–3 months (full feature set, hardened) |
| Primary Challenges | LinkedIn access, email deliverability, non-generic AI outputs |
| Biggest Ongoing Risk | Platform policy changes (LinkedIn, Gmail) invalidating components |
| Ongoing Maintenance | 2–4 hours/week once stable; higher during platform changes |

---

## Appendix A — Glossary

| Term | Definition |
|---|---|
| Canonical Resume | The single authoritative version of the resume, stored as structured JSON, from which all tailored versions are derived |
| Workflow Engine | Software (e.g. Temporal, Celery) that manages multi-step automated processes with retry logic and state persistence |
| Embedding | A numerical vector representation of text, used for similarity comparisons without requiring keyword matching |
| Human-in-the-Loop | A design pattern where automated systems pause and request human review before taking consequential actions |
| Semi-Agent | An AI-augmented system that follows deterministic pipelines but delegates specific reasoning tasks to AI models |
| Rule-based Filter | A code-only decision step using explicit criteria (location, salary, keywords) to include or exclude jobs without AI |
| Cache Hit | When a requested AI output already exists in storage and is returned without calling the AI API again |
| Temporal | An open-source workflow orchestration platform providing durable, fault-tolerant execution of multi-step processes |
| Playwright | A browser automation library that can render JavaScript-heavy websites and interact with authenticated sessions |
| IMAP | Internet Message Access Protocol; used to read and monitor email inboxes programmatically |

---

*AI-Powered Job Application Automation System — Architecture Guide*
*Internal Document — Version 1.0*