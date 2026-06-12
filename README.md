<div align="center">

# AURA — Universal Data Engine

### Raw data in. Intelligence out.

**A full-stack data intelligence platform that ingests any messy file, cleans and profiles it automatically, lets you interrogate it through streaming AI chat, and delivers a branded Data Intelligence Report — all in a five-step pipeline.**

[![GitHub](https://img.shields.io/badge/GitHub-skayy47%2FAURA-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/skayy47/AURA)
[![Python](https://img.shields.io/badge/Python-3.11-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178c6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
![i18n](https://img.shields.io/badge/i18n-EN_%7C_AR_RTL-6C3FE5?style=for-the-badge)
[![CI](https://github.com/skayy47/AURA/actions/workflows/ci.yml/badge.svg)](https://github.com/skayy47/AURA/actions/workflows/ci.yml)

</div>

---

## What AURA does

You drop a CSV, Excel, JSON, or Parquet file:

| Step | Route | What actually happens |
|---|---|---|
| 📂 **Ingest** | `/ingest` | Auto-detected encoding, type inference, 200 MB guard, 5-row preview |
| 🧼 **Clean** | `/clean` | 8-step pipeline — normalize names, coerce types, dedupe, impute, outlier flags. Every change logged, diff shown. |
| 🔍 **Explore** | `/explore` | Auto-generated Plotly charts: histograms, scatter, correlation heatmap, missing-value map, per-column profiles |
| 🤖 **AI Chat** | `/ai-chat` | Ask questions in natural language — streamed token-by-token. Claude, GPT-4o, or Groq (free default). AI never sees raw rows. |
| 📄 **Export** | `/docs` | CSV · XLSX · JSON · Parquet · branded **PDF Data Intelligence Report** (real headless render, not a screenshot) |

**No sign-up. No database. In-memory, session-scoped (4h TTL).**

---

## Why it's technically interesting

### 1 · Multi-provider AI with free-first cascade

A single `PROVIDERS` registry is the source of truth for all AI integrations. `resolve_provider()` tries Groq (free) first, then OpenAI, then Claude — whichever is configured. Groq and OpenAI share one call path (OpenAI-compatible `base_url`); Claude uses the Anthropic SDK. Adding a new provider is one dictionary entry, nothing else.

`executive_summary()` (called during PDF generation) cascades further: if no LLM is reachable, it builds a deterministic textual summary from the stats payload so **the PDF always renders** — even with no API keys configured.

---

### 2 · Ranked insight engine — above raw stats

`/api/analyze` is not a describe() wrapper. It runs a scoring pass that surfaces things like:

- High-cardinality string columns that should not be treated as categories
- Columns with |skew| > 2 that invalidate mean-based analysis
- Columns with >20% nulls flagged as structural data quality issues  
- Numeric pairs with |r| > 0.7 surfaced as correlation candidates

Each observation is ranked. The UI shows the top three with actionable framing. The endpoint result is cached after the first call — subsequent chart renders don't re-run the analysis.

---

### 3 · Real PDF generation (headless Chromium, not a screenshot)

`POST /api/export/pdf` calls `pdf_renderer.py`:

1. `build_report_context()` assembles the stats payload, ranked insights, and chart SVG specs into a Jinja2 context dict.
2. The `report.html.j2` template is rendered to an HTML string in memory.
3. Playwright's `page.set_content()` + `page.pdf()` renders it via headless Chromium.

The output is a paginated, fully styled PDF with the AURA brand, dataset summary, insight section, and chart thumbnails. It works because Chromium does the layout. The `Dockerfile` bakes in Playwright + Chromium so it works cold on any host.

---

### 4 · SSE streaming end-to-end (FastAPI → Next.js)

The AI chat endpoint streams tokens from the model through to the browser with zero polling:

```
FastAPI async generator → StreamingResponse(media_type="text/event-stream")
    → Next.js fetch() + ReadableStream
        → Zustand store (token append)
            → React component (live bubble render)
```

This works across all three AI providers — each has a different SDK streaming API; `ai_insights.py` normalizes them into a single async generator interface.

---

### 5 · Bilingual interface (EN / AR RTL) — production-grade i18n

Every string in the app is keyed through `next-intl v4`. The URL path carries the locale: `/en/explore` · `/ar/explore`. Arabic flips the entire layout to RTL including sidebar, data tables, chart labels, and form fields. 220+ translation keys, maintained in `messages/en.json` and `messages/ar.json`.

This is not a "toggle language" demo — it's a proper RTL-aware layout with bidirectional Tailwind utilities throughout.

---

## Architecture

```
  File Upload (CSV / TSV / XLSX / JSON / Parquet)
       │
       ▼
  ┌────────────────────────────────────────────────────────────────────┐
  │  AURA-BACKEND  (FastAPI v5.0 · Python 3.11 · Uvicorn)             │
  │                                                                    │
  │  POST /api/ingest   → engines/ingestion.py  → IngestResult        │
  │  POST /api/clean    → engines/cleaning.py   → (df, log)           │
  │  GET  /api/explore  → engines/exploration.py → Plotly JSON specs  │
  │  GET  /api/analyze  → engines/analysis.py   → ranked insights     │
  │  POST /api/ask      → engines/ai_insights.py → SSE token stream   │
  │  POST /api/export/pdf → services/pdf_renderer.py                  │
  │                         (Jinja2 → Playwright → PDF bytes)         │
  │                                                                    │
  │  api/deps.py   UUID session store · 4h TTL · in-memory            │
  └──────────────────┬─────────────────────────────────────────────────┘
                     │ REST + SSE
                     ▼
  ┌────────────────────────────────────────────────────────────────────┐
  │  AURA-FRONTEND  (Next.js 14 App Router · TypeScript · Tailwind)   │
  │                                                                    │
  │  /[locale]/ingest   upload + session init                         │
  │  /[locale]/clean    cleaning config + live diff view              │
  │  /[locale]/explore  5-tab Plotly explorer                         │
  │  /[locale]/ai-chat  streaming chat interface                      │
  │  /[locale]/docs     inline documentation                          │
  │  /[locale]/pricing  tier overview + Stripe checkout               │
  │                                                                    │
  │  lib/api.ts    typed REST + SSE client                            │
  │  lib/store.ts  Zustand session state                              │
  │  next-intl     EN / AR RTL routing + layout                       │
  └────────────────────────────────────────────────────────────────────┘
```

---

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| **Backend** | FastAPI 0.111 + Python 3.11 | Async, typed, OpenAPI auto-docs |
| **Data** | Pandas 2.2 + Plotly | Industry standard; Plotly specs ship to the frontend as JSON |
| **AI** | Groq (free default) / OpenAI / Claude | Single registry; free-first cascade; zero lock-in |
| **PDF** | Playwright + Jinja2 | Real headless Chromium render — paginated, styled, not a screenshot |
| **Insights** | Custom `analysis.py` | Ranked, actionable observations — not just `df.describe()` |
| **Frontend** | Next.js 14 App Router + TypeScript | Full-stack TypeScript; locale-aware SSR routing |
| **State** | Zustand 5 | Lightweight, no boilerplate |
| **Styling** | Tailwind 3.4 + Framer Motion 12 | Dark "Luminal Void" palette (`#00E5FF` / `#8B5CF6` on `#030712`) |
| **i18n** | next-intl v4 | EN + AR RTL — 220+ keys, bidirectional layout |
| **Billing** | Stripe SDK | Checkout flow wired; entitlement persistence is v5.1 |
| **Testing** | pytest + ruff + black / tsc + Next build | Quality gates enforced in CI on both stacks |
| **Deploy** | HF Spaces Docker (backend) + Vercel (frontend) | Free-tier hosting; Dockerfile bakes Playwright+Chromium |

---

## Quick start

Requires Python 3.11+ and Node 18+.

```bash
git clone https://github.com/skayy47/AURA
cd AURA

# --- Backend ---
cd AURA-BACKEND
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
playwright install chromium     # PDF export only — skip if you don't need it

cp ../.env.example AURA-BACKEND/.env
# → edit .env, set GROQ_API_KEY at minimum (free, no card required)

uvicorn main:app --reload --port 8000
# API: http://localhost:8000 · Docs: http://localhost:8000/docs
```

```bash
# --- Frontend (new terminal) ---
cd AURA-FRONTEND
npm install
npm run dev
# → http://localhost:3000
```

Click **"Try with sample data"** on the landing page to load a pre-built MENA dataset with no upload needed.

---

## Environment variables

All backend secrets live in `AURA-BACKEND/.env` (gitignored — never committed).

AURA is **free-first**: it defaults to **Groq** and cascades to whatever paid keys are present. Only `GROQ_API_KEY` is needed for working AI.

| Variable | Tier | Description |
|---|---|---|
| `GROQ_API_KEY` | **Free · default** | [console.groq.com](https://console.groq.com/keys) — Llama 3.3 70B |
| `OPENAI_API_KEY` | Paid · optional | GPT-4o mini upgrade |
| `ANTHROPIC_API_KEY` | Paid · optional | Claude Sonnet 4.6 upgrade |
| `ALLOWED_ORIGINS` | — | Comma-separated CORS origins (e.g. `https://your-frontend.vercel.app`) |
| `STRIPE_SECRET_KEY` | Billing | Stripe dashboard → Developers → API keys |
| `STRIPE_WEBHOOK_SECRET` | Billing | Stripe dashboard → Webhooks |
| `STRIPE_PRICE_PRO_MONTHLY` | Billing | Price ID from Stripe products |
| `STRIPE_PRICE_TEAM_MONTHLY` | Billing | Price ID from Stripe products |
| `FRONTEND_URL` | Redirects | Defaults to `http://localhost:3000` |
| `PORT` | Deploy | `8000` local · `7860` on HF Spaces |

---

## Quality gates

Both stacks must pass before merge:

```bash
# Backend
cd AURA-BACKEND
ruff check . --select E,F,W --ignore E501
black --check .
pytest ../tests -q

# Frontend
cd AURA-FRONTEND
npx tsc --noEmit
npm run build
```

---

## Deployment

### Backend → Hugging Face Spaces (Docker, free)

The `Dockerfile` at repo root bakes in Playwright + Chromium — PDF export works cold on the Space with no extra setup.

```bash
git remote add space https://huggingface.co/spaces/<username>/aura-backend
git push space main
```

Set Space secrets: `GROQ_API_KEY`, `ALLOWED_ORIGINS`, `PORT=7860`.

### Frontend → Vercel

Set root directory to `AURA-FRONTEND`. Add one env var:

```
NEXT_PUBLIC_API_URL=https://<username>-aura-backend.hf.space
```

`NEXT_PUBLIC_*` vars are baked at build time — a change requires a redeploy.

---

## CI / CD

`.github/workflows/ci.yml` runs on every push to `main`:

| Job | Steps |
|---|---|
| **backend** | ruff lint · black check · pytest |
| **frontend** | TypeScript type check · `next build` |
| **e2e smoke** | Playwright: boots both services, hits `/health` |
| **deploy gate** | All jobs must pass |

---

## Project structure

```
AURA/
├── AURA-BACKEND/
│   ├── main.py                     FastAPI app + CORS + load_dotenv
│   ├── api/
│   │   ├── deps.py                 UUID session store (4h TTL, in-memory)
│   │   ├── models.py               Pydantic request / response contracts
│   │   └── routes/                 ingest · clean · explore · ai · export · samples · billing
│   ├── engines/
│   │   ├── ingestion.py            load_file_bytes() → IngestResult
│   │   ├── cleaning.py             clean_dataframe() → (df, log) + quality score
│   │   ├── exploration.py          profile_dataframe() + Plotly chart specs
│   │   ├── analysis.py             ranked insights, segments, trends (cached)
│   │   └── ai_insights.py          multi-provider chat + executive_summary()
│   ├── services/
│   │   ├── pdf_renderer.py         Jinja2 + Playwright → PDF bytes
│   │   └── billing.py              Stripe checkout session
│   ├── templates/report.html.j2    Data Intelligence Report template
│   └── static/samples/             3 MENA demo datasets (no upload required)
│
├── AURA-FRONTEND/
│   └── src/
│       ├── app/[locale]/           landing · ingest · clean · explore · ai-chat · docs · pricing
│       ├── components/             ai · background · clean · explore · landing · layout · ui
│       └── lib/
│           ├── api.ts              Typed REST + SSE client
│           ├── store.ts            Zustand session state
│           └── tier.ts             Feature-gate logic
│
├── tests/                          pytest suites (ingestion · cleaning · exploration)
├── messages/                       en.json · ar.json (~220 keys each)
├── Dockerfile                      Backend image (Playwright + Chromium baked)
├── .github/workflows/ci.yml        Full CI pipeline
└── .env.example                    Environment variable template
```

---

## Roadmap

| Version | Status | What's in it |
|---|---|---|
| **v5.0** | ✅ Shipped | 3D landing, bilingual EN/AR RTL, Stripe checkout, E2E CI, PDF report, ranked insight engine |
| **v5.1** | 🔜 Planned | Entitlement persistence; Redis session store for multi-worker support |
| **v6.0** | 💡 Future | Live public demo URL; agent mode (multi-step analysis plans) |

---

## Security

- API keys are never committed — `.env` is gitignored, only `.env.example` ships.
- Keys are lazy-initialized at request time — `pytest` and `next build` pass with zero env vars.
- No database — sessions are in-memory with a 4h TTL. No user data persists between restarts.
- CORS is env-driven via `ALLOWED_ORIGINS` — no hardcoded wildcards in production.

---

<div align="center">

Built by **[Oussama Skia (SKAY)](https://github.com/skayy47)** — AI Engineer · Data Scientist

*AURA demonstrates full-stack AI product engineering: typed REST APIs, SSE streaming, real PDF generation,*  
*multi-provider AI orchestration, bilingual RTL UI, and a production-grade CI/CD pipeline.*  
*Not a notebook export — a deployable data product.*

</div>
