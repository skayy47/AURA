# ⚡ AURA — Universal Data Engine

> Ingest · Clean · Explore · AI Insights · Export · Arabic UI · PDF Reports

![Next.js](https://img.shields.io/badge/Next.js-14-000000?logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-3.4-38BDF8?logo=tailwindcss&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-Sonnet_4.6-7C3AED)
![i18n](https://img.shields.io/badge/i18n-EN_%7C_AR-6C3FE5)
![License](https://img.shields.io/badge/License-MIT-10B981)

---

## What is AURA?

AURA is a full-stack data platform that takes you from a raw file upload to AI-powered insights in minutes. Upload any structured dataset, auto-clean it with an 8-step pipeline, explore interactive charts, ask Claude or GPT-4o about it in natural language, and export a branded PDF report — or a clean CSV/Excel/JSON/Parquet file.

**V4 ships four GTM features:**

| Feature | What it is |
|---------|------------|
| 🌐 **Arabic UI + RTL** | Full EN ↔ AR toggle. Tailwind logical props, mirrored charts, Arabic numerics via `Intl.NumberFormat`. |
| 📄 **PDF Report Export** | Playwright renders a branded dark-theme PDF — summary metrics, column profiles, correlation pairs, cleaning log. |
| 🗂️ **Sample Datasets** | Three pre-loaded real-world CSVs (sales, climate, MENA orders) — no upload needed to try AURA. |
| 💳 **Stripe Billing** | Checkout, portal, and webhook endpoints. Free / Pro ($29) / Team ($99) tiers with `<ProGate>` component. |

---

## Architecture

```
┌──────────────────────────┐      REST + SSE        ┌──────────────────────────┐
│  AURA-FRONTEND (3000)    │ ─────────────────────▶ │  AURA-BACKEND (8000)     │
│  Next.js 14 · React 18   │                        │  FastAPI · Uvicorn       │
│  next-intl v4 (EN/AR)    │ ◀───────────────────── │  Pandas · Anthropic SDK  │
│  Tailwind · Zustand       │       JSON / stream    │  Playwright · Jinja2     │
│  Framer Motion · Recharts│                        │  Stripe SDK              │
└──────────────────────────┘                        └──────────────────────────┘
```

- All data, AI, and rendering happen on the backend — the frontend is a pure client.
- Sessions are UUID-keyed, in-memory, 4-hour TTL (no database required).
- AI responses stream over SSE for token-by-token rendering.
- Locale is part of the URL path: `/en/ingest` · `/ar/ingest`.

---

## Pipeline

| Step | Route | What it does |
|------|-------|--------------|
| 📂 **Ingest** | `/ingest` | CSV · XLSX · JSON · Parquet · TSV — encoding auto-detected, type inference, 5-row preview |
| 🧼 **Clean** | `/clean` | 8-step pipeline: normalize names, drop empty cols, clean strings, promote types, dedupe, impute, flag outliers, quality score |
| 🔍 **Explore** | `/explore` | Auto-generated histograms, scatter plots, correlation heatmap, missing-value map, column profiles |
| 🤖 **AI Chat** | `/ai-chat` | Claude Sonnet 4.6 or GPT-4o with SSE streaming — full dataset context injected |
| 📄 **Docs** | `/docs` | Export to CSV · XLSX · JSON · Parquet · **PDF report** |

---

## Quick Start

Requires Python 3.11+ and Node 18+.

**1. Clone and set up environment**
```bash
git clone https://github.com/skayy47/AURA
cd AURA

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

cp AURA-BACKEND/.env.example AURA-BACKEND/.env  # add your API keys
```

**2. Start the backend (terminal 1)**
```bash
cd AURA-BACKEND
pip install -r requirements.txt
playwright install chromium      # for PDF export
uvicorn main:app --reload --port 8000
```

**3. Start the frontend (terminal 2)**
```bash
cd AURA-FRONTEND
npm install
npm run dev
```

Open **http://localhost:3000** — the marketing landing page. Click "Try with sample data" to load a pre-built dataset instantly, or upload your own CSV.

Backend health: **http://localhost:8000/health** · Interactive API docs: **http://localhost:8000/docs**

---

## Environment Variables

Backend reads from `AURA-BACKEND/.env`:

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | For Claude | [console.anthropic.com](https://console.anthropic.com/) |
| `OPENAI_API_KEY` | For GPT-4o | [platform.openai.com](https://platform.openai.com/api-keys) |
| `STRIPE_SECRET_KEY` | For billing | Stripe dashboard → Developers → API keys |
| `STRIPE_WEBHOOK_SECRET` | For webhooks | Stripe dashboard → Webhooks |
| `STRIPE_PRICE_PRO_MONTHLY` | For Pro tier | Price ID from Stripe products |
| `STRIPE_PRICE_TEAM_MONTHLY` | For Team tier | Price ID from Stripe products |
| `FRONTEND_URL` | For redirects | Defaults to `http://localhost:3000` |
| `POPPLER_PATH` | For PDF OCR | Windows only — path to Poppler `bin/` |
| `DEBUG` | No | `1` to enable debug logging |

Frontend reads `NEXT_PUBLIC_API_URL` from `AURA-FRONTEND/.env.local` (defaults to `http://localhost:8000`).

---

## REST API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/health` | Liveness probe |
| `POST` | `/api/ingest` | Multipart upload → `{session_id, meta, preview}` |
| `POST` | `/api/clean` | Run 8-step cleaning pipeline |
| `GET` | `/api/explore/{session_id}` | Profile + chart recommendations |
| `POST` | `/api/ask` | AI chat (SSE stream) |
| `GET` | `/api/export/{session_id}/{format}` | Download cleaned dataset |
| `POST` | `/api/export/pdf` | Generate branded PDF report |
| `GET` | `/api/samples` | List 3 sample dataset slugs |
| `GET` | `/api/samples/{slug}/download` | Download sample CSV |
| `POST` | `/api/samples/{slug}/load` | Load sample into session |
| `POST` | `/api/billing/checkout` | Create Stripe Checkout Session |
| `POST` | `/api/billing/portal` | Create Stripe Customer Portal session |
| `POST` | `/api/billing/webhook` | Receive Stripe webhook events |

Full OpenAPI schema: **http://localhost:8000/docs**

---

## Arabic / RTL Support

AURA ships full bilingual support via **next-intl v4**. Switch languages with the EN | عربي toggle in the top bar — it preserves your current page and session.

Technical details:
- Locale prefix routing: `/en/*` · `/ar/*`
- Tailwind logical properties throughout (`ms-`, `ps-`, `start-`, `border-s`, etc.)
- `<html dir="rtl">` set by `[locale]/layout.tsx`
- Recharts Y-axis mirrored (`orientation="right"`) in RTL mode
- `Intl.NumberFormat(locale)` for all numeric display in charts

---

## PDF Report Export

Click **Export PDF** on the Explore page. The backend:

1. Builds a report context from the session profile + cleaning log
2. Renders `templates/report.html.j2` (Jinja2 dark-themed template)
3. Converts to PDF via Playwright Chromium (headless)
4. Streams `application/pdf` back to the browser

The report includes: summary metrics, full column profiles table, top correlation pairs, and the cleaning pipeline log.

**Requires:** `playwright install chromium` after `pip install -r requirements.txt`.

---

## Sample Datasets

Three real-world datasets are pre-loaded at `AURA-BACKEND/static/samples/`:

| Slug | Title | Rows | Notable issues |
|------|-------|------|---------------|
| `sales-mess` | Sales Pipeline (messy) | 40 | Duplicate rows, outlier price, missing fields |
| `climate-sensors` | MENA Climate Sensors | 44 | Time series, sensor outlier, one missing temp |
| `mena-orders` | MENA E-Commerce Orders | 50 | Clean — good for category / bar chart exploration |

Load via `POST /api/samples/{slug}/load` or click **Load & Explore** on the landing page.

---

## Project Structure

```
AURA/
├── AURA-BACKEND/
│   ├── main.py                    CORS + router registration
│   ├── api/
│   │   ├── deps.py                In-memory session store (UUID → state, 4h TTL)
│   │   ├── models.py              Pydantic schemas
│   │   └── routes/
│   │       ├── ingest.py          POST /api/ingest
│   │       ├── clean.py           POST /api/clean
│   │       ├── explore.py         GET  /api/explore/{sid}
│   │       ├── ai.py              POST /api/ask (SSE)
│   │       ├── export.py          GET  /api/export/{sid}/{fmt} + POST /api/export/pdf
│   │       ├── samples.py         GET/POST /api/samples/*
│   │       └── billing.py         POST /api/billing/{checkout,portal,webhook}
│   ├── engines/                   Pure-Python domain logic
│   │   ├── ingestion.py           V3.3 IngestResult + FileMeta
│   │   ├── cleaning.py            V3.4 8-cleaner orchestrator + quality score
│   │   ├── exploration.py         V3.5 profile_dataframe + recommend_charts
│   │   ├── ai_insights.py         Claude + OpenAI streaming
│   │   ├── ocr.py                 Tesseract + Poppler
│   │   └── audio_video.py         Whisper + librosa + OpenCV
│   ├── services/
│   │   ├── pdf_renderer.py        Playwright + Jinja2 PDF renderer
│   │   └── billing.py             Stripe checkout / portal / webhook
│   ├── templates/
│   │   └── report.html.j2         Dark-theme PDF report template
│   └── static/samples/            Pre-loaded CSV datasets
│
├── AURA-FRONTEND/
│   ├── src/app/[locale]/          Locale-prefixed App Router routes
│   │   ├── page.tsx               Marketing landing page
│   │   ├── ingest/ clean/
│   │   ├── explore/               + Export PDF button
│   │   ├── ai-chat/ docs/
│   │   ├── pricing/               Pricing tiers + Stripe checkout
│   │   └── billing/success|cancel
│   ├── src/components/
│   │   ├── explore/ExportPDFButton.tsx
│   │   └── ui/ProGate.tsx         Tier-gated feature overlay
│   ├── src/lib/tier.ts            useTier() hook (free/pro/team)
│   ├── src/i18n/                  next-intl routing + navigation
│   ├── messages/en.json           English strings (~140 keys)
│   └── messages/ar.json           Arabic translations
│
├── tests/                         Pytest suites
└── LICENSE                        MIT
```

---

## Tests

```bash
cd AURA-BACKEND
python -m pytest ../tests -v
```

---

## Tech Stack

**Frontend**
- Next.js 14 (App Router) · React 18 · TypeScript 5
- next-intl v4.11 (EN/AR, locale routing, RTL)
- Tailwind CSS 3.4 — Luminal Void tokens + logical properties
- Zustand 5 · Framer Motion 12 · Recharts 3

**Backend**
- FastAPI 0.111 · Uvicorn · Pydantic 2
- Pandas 2.2 · NumPy · OpenPyXL · PyArrow
- Anthropic SDK (Claude Sonnet 4.6) · OpenAI SDK
- Playwright 1.45 + Jinja2 3.1 (PDF rendering)
- Stripe 9.9 (billing)
- Tesseract + Poppler (OCR) · Whisper · librosa · OpenCV

**Design System — "Luminal Void"**

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | `#040712` | App background |
| `--surface` | `#0A1022` | Cards |
| `--aurora-purple` | `#6C3FE5` | Primary accent |
| `--aurora-cyan` | `#22D3EE` | Secondary accent |
| `--text` | `#F1F5F9` | Primary text |
| `--green` | `#10B981` | Success / quality |
| `--amber` | `#F59E0B` | Warnings |

---

## Legacy Streamlit App

The original Streamlit V2.1 is preserved at the repo root (`app.py`, `pages/`, `engines/`, `state/`, `utils/`). It is not the recommended path — Next.js + FastAPI is the canonical V3/V4 stack. Run it with `streamlit run app.py` for reference.

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built by [SKAY](https://github.com/skayy47) · Powered by Claude*
