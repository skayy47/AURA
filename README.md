# ⚡ AURA — Universal Data Engine

> Ingest · Clean · Explore · AI-Powered Insights

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## What it does

AURA is a Streamlit-powered data platform that takes you from raw file upload to
AI-powered insights in minutes. Upload any structured dataset, apply configurable
auto-cleaning, explore interactive Plotly charts, and ask natural-language
questions via Claude Sonnet 4.6 or GPT-4o-mini — all in one dark-themed UI.

---

## Features

- 📂 **Ingest** CSV, Excel, JSON, Parquet, TSV — with encoding auto-detection and multi-sheet warnings
- 🧼 **Configurable cleaning** — rename columns, fill missing, drop duplicates, detect dates, with full change log
- 🔍 **Interactive exploration** — histograms, box plots, correlation heatmaps, missing-value heatmaps via Plotly
- 🤖 **AI insights** via Claude Sonnet 4.6 (Anthropic) or GPT-4o-mini (OpenAI), fully streaming
- 📄 **OCR** — extract text from PDFs using Tesseract + Poppler
- 🎵 **Audio transcription** with OpenAI Whisper + librosa feature extraction
- 🎞 **Video frame extraction** using OpenCV
- ⬇️ **Multi-format export** — CSV, Excel (styled), JSON, Parquet

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/AURA
cd AURA
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # then add your API keys
streamlit run app.py
```

---

## Environment Variables

See [`.env.example`](.env.example) — you need **at least one** AI key to use the chat page.

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | For Claude | From [console.anthropic.com](https://console.anthropic.com/) |
| `OPENAI_API_KEY` | For GPT | From [platform.openai.com](https://platform.openai.com/api-keys) |
| `POPPLER_PATH` | For PDF OCR | Path to Poppler `bin/` folder |
| `DEBUG` | No | Set `1` to enable debug mode |

---

## Project Structure

```
AURA/
├── app.py                      # Landing / home page
├── pages/
│   ├── 1_📂_Ingest.py
│   ├── 2_🧼_Clean.py
│   ├── 3_🔍_Explore.py
│   ├── 4_🤖_AI_Chat.py
│   └── 5_📄_Documents.py
├── engines/
│   ├── ingestion.py            # CSV/TSV/Excel/JSON/Parquet loader
│   ├── cleaning.py             # CleaningConfig + logged clean_dataframe()
│   ├── exploration.py          # Profiling + Plotly chart helpers
│   ├── ai_insights.py          # ask_ai() — Claude & OpenAI, streaming
│   ├── ocr.py                  # PDF → text via Tesseract
│   └── audio_video.py          # Whisper transcription, librosa, OpenCV
├── state/
│   └── session.py              # Centralised AuraSession dataclass
├── utils/
│   ├── config.py               # .env helpers
│   ├── helpers.py              # Logger factory, df_to_csv_bytes
│   └── exporters.py            # to_csv/excel/json/parquet → bytes
├── assets/
│   └── css/aura.css            # Dark glassmorphism design system
├── tests/
│   ├── test_ingestion.py
│   ├── test_cleaning.py
│   └── test_exploration.py
├── poppler-25.11.0/            # Bundled Poppler (Windows)
├── requirements.txt
└── .env.example
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Tech Stack

Python 3.11 · Streamlit · Pandas · Plotly · OpenAI Whisper · Anthropic Claude ·
Tesseract OCR · librosa · OpenCV · openpyxl · pyarrow
