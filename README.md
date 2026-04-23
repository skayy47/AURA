# ⚡ AURA — Universal Data Engine

> Ingest · Clean · Explore · AI Insights · Export

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-Sonnet_4.6-7C3AED)
![License](https://img.shields.io/badge/License-MIT-10B981)

---

## What is AURA?

AURA is a full-stack data platform that takes you from a raw file upload to AI-powered insights in minutes. Built with a dark Luminal Void design system, it combines a configurable data pipeline with streaming AI chat — all in a single, cohesive UI.

Upload any structured dataset → auto-clean it → explore interactive charts → ask natural-language questions via Claude Sonnet or GPT-4o-mini → export in any format.

---

## Features

| Step | What it does |
|------|-------------|
| 📂 **Ingest** | CSV · Excel · JSON · Parquet · TSV — with encoding auto-detection |
| 🧼 **Clean** | Rename columns, fill missing, drop duplicates, detect dates — full change log |
| 🔍 **Explore** | Histograms, box plots, correlation heatmap, missing-value pattern via Plotly |
| 🤖 **AI Chat** | Claude Sonnet 4.6 or GPT-4o-mini with streaming — ask anything about your data |
| 📄 **Docs** | PDF OCR (Tesseract), audio transcription (Whisper), video frame extraction |
| ⬇️ **Export** | CSV · Excel (styled) · JSON · Parquet |

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/AURA
cd AURA

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env        # add your API keys
streamlit run app.py
```

Then open `http://localhost:8501` and upload `data/samples/employees_sample.csv` to try it immediately.

---

## Environment Variables

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | For Claude | [console.anthropic.com](https://console.anthropic.com/) |
| `OPENAI_API_KEY` | For GPT-4o-mini | [platform.openai.com](https://platform.openai.com/api-keys) |
| `POPPLER_PATH` | For PDF OCR | Path to Poppler `bin/` folder — Windows only |
| `DEBUG` | No | Set `1` to enable debug logging |

At least one AI key is required for the AI Chat page. All other features work without any keys.

---

## Project Structure

```
AURA/
├── app.py                      # Landing page
├── pages/
│   ├── 1_📂_Ingest.py          # File upload + validation
│   ├── 2_🧼_Clean.py           # Configurable auto-cleaning
│   ├── 3_🔍_Explore.py         # Interactive charts
│   ├── 4_🤖_AI_Chat.py         # Streaming AI chat
│   └── 5_📄_Documents.py       # OCR · Audio · Video · Export
├── engines/
│   ├── ingestion.py            # Multi-format file loader
│   ├── cleaning.py             # CleaningConfig + clean_dataframe()
│   ├── exploration.py          # Profiling + Plotly chart helpers
│   ├── ai_insights.py          # ask_ai() — Claude & OpenAI, streaming
│   ├── ocr.py                  # PDF → text via Tesseract + Poppler
│   └── audio_video.py          # Whisper transcription, librosa, OpenCV
├── state/
│   └── session.py              # Centralised AuraSession dataclass
├── utils/
│   ├── config.py               # .env loader helpers
│   ├── helpers.py              # Logger, CSS loader, UI helpers
│   └── exporters.py            # to_csv / to_excel / to_json / to_parquet
├── assets/
│   └── css/aura.css            # Luminal Void design system
├── data/
│   └── samples/
│       └── employees_sample.csv  # Demo dataset — 25 rows, 10 cols
├── AURA-BACKEND/               # FastAPI backend (in development)
├── AURA-FRONTEND/              # Next.js 14 frontend (in development)
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

---

## Running Tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

---

## Tech Stack

**Frontend:** Streamlit 1.40+ · Plotly · Custom CSS (Luminal Void design system)

**Backend engines:** Python 3.11 · Pandas · NumPy · OpenPyXL · PyArrow

**AI:** Anthropic Claude Sonnet 4.6 · OpenAI GPT-4o-mini

**OCR / Media:** Tesseract · Poppler · OpenAI Whisper · librosa · OpenCV

---

## Design System

AURA uses the **Luminal Void** aesthetic — a dark-void palette with bioluminescent purple accents and surgical typography. Color tokens, spacing, and component classes are defined in `assets/css/aura.css`.

| Token | Value | Usage |
|-------|-------|-------|
| Background | `#040712` | App background |
| Surface | `#0A1022` | Card backgrounds |
| Purple | `#6C3FE5` | Primary accent |
| Green | `#10B981` | Success states |
| Amber | `#F59E0B` | Warnings / missing data |
| Text | `#F1F5F9` | Primary text |

---

## License

MIT — see [LICENSE](LICENSE)
