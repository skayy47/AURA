# ⚡ AURA — Universal Data Engine

> **Ingest · Clean · Explore · AI Insights · Export** — from raw CSV to boardroom PDF in five minutes.

![Next.js](https://img.shields.io/badge/Next.js-14-000000?logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-3.4-38BDF8?logo=tailwindcss&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-Sonnet_4.6-7C3AED)
![i18n](https://img.shields.io/badge/i18n-EN_%7C_AR-6C3FE5)
[![CI](https://github.com/skayy47/AURA/actions/workflows/ci.yml/badge.svg)](https://github.com/skayy47/AURA/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/License-MIT-10B981)

AURA is a full-stack data platform that takes you from a raw file upload to AI-powered insights in minutes. Upload any structured dataset, auto-clean it with an 8-step pipeline, explore interactive charts, ask Claude or GPT-4o in natural language, and export a branded PDF report — all through a bilingual (EN/AR) production-grade interface.

**No sign-up. No database. In-memory, session-scoped.**

---

## What it does

| Step | Route | Capability |
|------|-------|-----------|
| 📂 **Ingest** | `/ingest` | CSV · XLSX · JSON · Parquet · TSV — encoding auto-detected, type inference, 5-row preview |
| 🧼 **Clean** | `/clean` | 8-step pipeline: normalize names, drop empty cols, clean strings, promote types, dedupe, impute, flag outliers, quality score |
| 🔍 **Explore** | `/explore` | Auto-generated histograms, scatter, correlation heatmap, missing-value map, column profiles |
| 🤖 **AI Chat** | `/ai-chat` | Claude Sonnet 4.6 or GPT-4o with SSE streaming — full dataset context injected |
| 📄 **Export** | `/docs` | CSV · XLSX · JSON · Parquet · **branded PDF report** (Playwright + Jinja2) |

---

## Architecture

```
┌──────────────────────────┐      REST + SSE        ┌──────────────────────────┐
│  AURA-FRONTEND (3000)    │ ─────────────────────▶ │  AURA-BACKEND (8000)     │
│  Next.js 14 · App Router │                        │  FastAPI 0.111 · Uvicorn │
│  next-intl v4 (EN/AR)    │ ◀───────────────────── │  Pandas · Anthropic SDK  │
│  Tailwind · Zustand       │       JSON / stream    │  Playwright + Jinja2     │
│  Framer Motion 12 (3D)   │                        │  Stripe SDK              │
└──────────────────────────┘                        └──────────────────────────┘
```

- All data, AI, and rendering happen on the **backend** — the frontend is a pure client.
- Sessions are UUID-keyed, **in-memory**, 4-hour TTL (no database required).
- AI responses **stream over SSE** for token-by-token rendering.
- Locale is part of the URL path: `/en/ingest` · `/ar/ingest`.
- CORS origins are env-driven via `ALLOWED_ORIGINS`.

---

## V5 Highlights

| Feature | Details |
|---------|---------|
| 🤖 **3D Robot Landing** | `<AuraBot>` enters with spring-driven 3D choreography — `rotateX -45°→0°`, `scale 0.7→1`. Mouse parallax adds ±10° tilt. |
| 🔁 **Scroll-Triggered Handoff** | Robot transitions via Framer Motion `layoutId` from hero into the persistent `<BotOrb>` chat button — one continuous visual thread. |
| 🎨 **Aurora "Luminal Void" Theme** | `#6c3fed` purple · `#22d3ee` cyan · `#3b82f6` blue — gradient text, bento cards, grain overlay, pulse-pill badges. |
| 📐 **11-Section Landing** | Hero · Pain Points · Live Demo Strip · Bento Steps · Samples · Output Preview · Tech Stack · Pricing · FAQ · Final CTA · Footer — fully i18n'd EN/AR. |
| 🌍 **Full Arabic UI** | RTL layout, Arabic translations for all 220+ string keys via next-intl v4. |
| 🧪 **E2E CI** | GitHub Actions: ruff · black · pytest (backend) + tsc · next build (frontend) + Playwright smoke (boots both services). |

---

## Quick Start

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
playwright install chromium     # for PDF export only
cp ../.env.example AURA-BACKEND/.env  # fill in API keys
uvicorn main:app --reload --port 8000

# --- Frontend (new terminal) ---
cd AURA-FRONTEND
npm install
npm run dev
```

Open **http://localhost:3000** → click **"Try with sample data"** to load a pre-built MENA dataset, or upload your own CSV.

> **Health check:** http://localhost:8000/health
> **API docs:** http://localhost:8000/docs

---

## Environment Variables

All backend secrets live in `AURA-BACKEND/.env` (gitignored — never commit):

AURA is **multi-provider, free-first**: it defaults to **Groq (free)** and falls
back across whatever keys are present. Claude / OpenAI are optional paid upgrades.

| Variable | Tier | Description |
|----------|------|-------------|
| `GROQ_API_KEY` | **Free · default** | [console.groq.com](https://console.groq.com/keys) — Llama 3.3 70B |
| `OPENAI_API_KEY` | Paid · optional | [platform.openai.com](https://platform.openai.com/) — GPT-4o mini |
| `ANTHROPIC_API_KEY` | Paid · optional | [console.anthropic.com](https://console.anthropic.com/) — Claude Sonnet 4.6 |
| `ALLOWED_ORIGINS` | — | Comma-separated frontend URLs (e.g. `https://your-frontend.vercel.app`) |
| `STRIPE_SECRET_KEY` | Billing | Stripe dashboard → Developers → API keys |
| `STRIPE_WEBHOOK_SECRET` | Billing | Stripe dashboard → Webhooks |
| `STRIPE_PRICE_PRO_MONTHLY` | Billing | Price ID from Stripe products |
| `STRIPE_PRICE_TEAM_MONTHLY` | Billing | Price ID from Stripe products |
| `FRONTEND_URL` | Redirects | Defaults to `http://localhost:3000` |
| `PORT` | Deploy | Hosting port (default `8000`; HF Spaces requires `7860`) |

> **Billing note:** Stripe checkout is fully wired. Entitlement persistence (linking a completed payment to a session tier) is the next planned milestone.

---

## Deployment

AURA has a **monorepo** — backend and frontend deploy independently.

### Backend — Hugging Face Spaces (Docker, free)

A `Dockerfile` is included at the repo root. The image bakes in Playwright/Chromium so PDF export works cold. See [`deploy/huggingface.md`](deploy/huggingface.md) for the full runbook.

```bash
# Add the Space as a remote and push
git remote add space https://huggingface.co/spaces/<your-username>/aura-backend
git push space main
```

Set Space secrets: `GROQ_API_KEY` (free — the only one needed for working AI),
`ALLOWED_ORIGINS`, `PORT=7860`. Optionally add `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`.

### Frontend — Vercel

Set the **root directory** to `AURA-FRONTEND` and add one env var:

```
NEXT_PUBLIC_API_URL=https://<your-username>-aura-backend.hf.space
```

`NEXT_PUBLIC_*` vars are **baked at build time** — a change requires a redeploy.

---

## CI / CD

`.github/workflows/ci.yml` runs on every push to `main`:

| Job | Steps |
|-----|-------|
| **backend** | ruff lint · black format check · pytest |
| **frontend** | TypeScript type check · `next build` |
| **e2e smoke** | Playwright: boots both services, hits `/health` (main only) |
| **deploy gate** | All jobs must pass |

---

## Tech Stack

**Frontend:** Next.js 14 · React 18 · TypeScript 5 · next-intl v4 (EN/AR RTL) · Tailwind 3.4 · Zustand 5 · Framer Motion 12.38 · Recharts 3

**Backend:** FastAPI 0.111 · Uvicorn · Pydantic 2.7 · Pandas 2.2 · Anthropic SDK · OpenAI SDK 1.35 · Playwright + Jinja2 (PDF) · Stripe 9.9 · OpenCV-headless · Whisper · librosa

---

## Project Structure

```
AURA/
├── AURA-BACKEND/
│   ├── api/routes/        ingest · clean · explore · ai · export · billing · samples
│   ├── engines/           ingestion · cleaning · exploration · ai_insights · ocr · audio_video
│   ├── services/          billing (Stripe) · pdf_renderer (Playwright + Jinja2)
│   ├── state/session.py   UUID-keyed in-memory store (4h TTL)
│   ├── utils/             config · helpers · exporters
│   └── main.py            FastAPI entry point
├── AURA-FRONTEND/
│   ├── src/app/[locale]/  landing · ingest · clean · explore · ai-chat · docs · pricing · billing
│   ├── src/components/    ai · background · clean · explore · ingest · landing · layout · ui
│   ├── src/lib/           api client · Zustand store · tier hook · types
│   └── messages/          en.json · ar.json (~220 keys each)
├── tests/                 pytest suites
├── Dockerfile             backend image (Playwright baked in)
├── .github/workflows/     ci.yml
└── LICENSE
```

---

## Roadmap

| Version | Status | What's in it |
|---------|--------|-------------|
| **v5.0** | ✅ Shipped | 3D landing, aurora theme, bilingual UI, Stripe checkout, E2E CI |
| **v5.1** | 🔜 Planned | Entitlement persistence; externalize session state (Redis) for multi-worker support |
| **v6.0** | 💡 Future | Live deployed demo; agent mode (multi-step analysis plans) |

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built by [Oussama Skia (SKAY)](https://github.com/skayy47) · Powered by Claude*
