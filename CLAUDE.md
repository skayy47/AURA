# CLAUDE.md — AURA Project Intelligence

> Read before every session. Reflects the **current V5 architecture** (FastAPI + Next.js).
> The legacy Streamlit app is archived under `legacy/` and is NOT the active product.

---

## Identity

**AURA — Universal Data Engine.** Owner: Oussama Skia (SKAY).
**Stage:** V5 — shipped, deploy-ready, portfolio flagship.
Full-stack: raw file → clean → explore → AI chat → branded Data Intelligence Report (PDF).
No database; in-memory, session-scoped (4h TTL).

**Stack:** FastAPI · Python 3.11 · Pandas · Plotly · Playwright+Jinja2 (PDF) ·
multi-provider AI (Groq free-default / OpenAI / Claude) · Next.js 14 · React 18 ·
TypeScript · Tailwind · Framer Motion · Zustand · next-intl (EN/AR RTL).

---

## Run

```bash
# Backend
cd AURA-BACKEND
.venv\Scripts\activate            # Windows  (source .venv/bin/activate on *nix)
pip install -r requirements.txt
playwright install chromium       # PDF export only
cp ../.env.example .env           # set at least GROQ_API_KEY (free)
uvicorn main:app --reload --port 8000

# Frontend
cd AURA-FRONTEND
npm install
cp .env.local.example .env.local  # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                       # http://localhost:3000
```

**Quality gates (must stay green):**
```bash
cd AURA-BACKEND && ruff check . --select E,F,W --ignore E501 && black --check . && pytest ../tests -q
cd AURA-FRONTEND && npx tsc --noEmit && npm run build
```

---

## Architecture (real)

```
AURA/
├── AURA-BACKEND/                 FastAPI
│   ├── main.py                   app + env-driven CORS (ALLOWED_ORIGINS) + load_dotenv
│   ├── api/
│   │   ├── deps.py               in-memory UUID session store (4h TTL)
│   │   ├── models.py             pydantic request/response models
│   │   └── routes/               ingest · clean · explore · ai · export · samples · billing
│   ├── engines/
│   │   ├── ingestion.py          load_file_bytes() → IngestResult (CSV/TSV/XLSX/JSON/Parquet)
│   │   ├── cleaning.py           clean_dataframe() → (df, log) + quality score
│   │   ├── exploration.py        profile_dataframe() + recommend_charts() (Plotly)
│   │   ├── analysis.py           analyze() → ranked insights, segments, trends, quality
│   │   ├── ai_insights.py        multi-provider chat + executive_summary() (free-first)
│   ├── services/
│   │   ├── pdf_renderer.py       build_report_context() + render_pdf() (Jinja2→Playwright)
│   │   └── billing.py            Stripe checkout (entitlement persistence = roadmap)
│   ├── templates/report.html.j2  Data Intelligence Report
│   └── static/samples/           3 MENA demo datasets
├── AURA-FRONTEND/                Next.js 14 App Router
│   └── src/
│       ├── app/[locale]/         landing · ingest · clean · explore · ai-chat · docs · pricing · billing
│       ├── components/           background(IntelligenceField) · ai · explore · docs · landing · layout · ui
│       └── lib/                  api.ts (REST+SSE) · store.ts (Zustand) · tier.ts
├── legacy/                       ⚠️ archived Streamlit V2 (do not import / not active)
├── Dockerfile                    backend image (Playwright+Chromium baked)
└── .github/workflows/ci.yml      backend lint+test · frontend tsc+build · e2e
```

---

## AI provider system (engines/ai_insights.py)

Single registry `PROVIDERS` = source of truth. **Groq (free) is the default**;
OpenAI/Claude are paid. Groq+OpenAI share one OpenAI-compatible path (base_url
differs); Claude uses the Anthropic SDK. `resolve_provider()` falls back to the
best *configured* provider (free first); `executive_summary()` cascades to a
deterministic summary if no provider is usable. Never send raw rows to the LLM
for the report — only the compact stats payload.

To add a provider: one entry in `PROVIDERS`. Nothing else.

---

## Key API endpoints

`POST /api/ingest` · `POST /api/clean` · `GET /api/explore/{sid}` ·
`GET /api/analyze/{sid}` (ranked insights, cached) · `POST /api/ask` (SSE chat) ·
`GET /api/ai/providers` · `GET /api/export/{sid}/{csv|xlsx|json|parquet}` ·
`POST /api/export/pdf` · `GET /health`.

---

## Conventions

- Backend: `from __future__ import annotations`, type hints, black (line 88-ish),
  ruff E/F/W clean, no bare `except`, structured logging not print.
- Sessions only via `api/deps.py` — never reach into the dict elsewhere.
- DataFrame truthiness trap: never `df = a or b` — use explicit `if x is None`.
- Frontend: TS strict, Tailwind tokens (2045 palette: cyan #00E5FF, violet #8B5CF6,
  blue #3B82F6, mint #00FFB2 on #030712), no emoji as icons (SVG/lucide), i18n keys.
- `.env` is gitignored — never commit keys.

---

## Environment

| Var | Tier | Purpose |
|-----|------|---------|
| `GROQ_API_KEY` | free · default | AI chat + report summaries (console.groq.com) |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | paid · optional | upgrades |
| `ALLOWED_ORIGINS` | — | comma-separated CORS origins |
| `PORT` | deploy | 8000 local / 7860 HF Spaces |
| `STRIPE_*` | optional | billing checkout |

---

## Deploy

Backend → Hugging Face Spaces (Docker, `Dockerfile` ready); Frontend → Vercel
(set `NEXT_PUBLIC_API_URL`). Secrets: `GROQ_API_KEY` is all that's needed for
working AI. See README "Deployment".

---

## Known / roadmap

- In-memory sessions = single-instance only (documented; fine for demo).
- Stripe entitlement persistence not wired (checkout flow only) — roadmap v5.1.
- PDF render needs Chromium (baked in Docker; blocked in some sandboxes).
