# CLAUDE.md — AURA Project Intelligence File
# This file is read automatically by Claude Code / Antigravity on every session.
# Keep it updated as the project evolves.

---

## Project Identity

**Name:** AURA — Universal Data Engine
**Owner:** SKAY (oussamaiskia@gmail.com)
**Stage:** V1 complete → V2 in progress
**Goal:** Portfolio flagship project. Ship V2, push to GitHub, then move on.
**Stack:** Python 3.11 · Streamlit · Pandas · Plotly · Anthropic Claude · OpenAI · Whisper · Tesseract OCR

---

## How to Run

```bash
# Activate venv (Windows)
.venv\Scripts\activate

# Run the app
streamlit run app.py

# Run tests
python -m pytest tests/ -v

# Lint
python -m ruff check .

# Format
python -m black .
```

Python interpreter: `C:\Users\Usuario\AppData\Local\Programs\Python\Python311\python.exe`
Virtual env: `.venv\Scripts\python.exe`
Poppler path: `C:\Users\Usuario\Desktop\AURA\poppler-25.11.0\Library\bin`

---

## Architecture — The Full Map

```
AURA/
├── app.py                    ← Landing page + routing (home only, no tab logic)
├── pages/
│   ├── 1_📂_Ingest.py        ← Upload, validate, store raw_df in session
│   ├── 2_🧼_Clean.py         ← CleaningConfig UI, cleaning log, side-by-side diff
│   ├── 3_🔍_Explore.py       ← Plotly charts: histogram, heatmap, box, timeseries
│   ├── 4_🤖_AI_Chat.py       ← Multi-provider AI (Claude + OpenAI), streaming
│   └── 5_📄_Documents.py     ← OCR (PDF), audio transcription, video frames
├── engines/
│   ├── ingestion.py          ← load_file() → (df, meta) — CSV/Excel/JSON/Parquet/TSV
│   ├── cleaning.py           ← clean_dataframe(df, config) → (df, log)
│   ├── exploration.py        ← stats + plotly chart functions
│   ├── ai_insights.py        ← ask_ai(df, question, provider) — Claude + OpenAI
│   ├── ocr.py                ← load_pdf_to_text() via Tesseract
│   └── audio_video.py        ← transcribe_audio(), extract_audio_features(), extract_frames_from_video()
├── state/
│   └── session.py            ← AuraSession dataclass + get_session() + reset_session()
├── utils/
│   ├── config.py             ← env vars: DEBUG, POPPLER_PATH, OPENAI_API_KEY, ANTHROPIC_API_KEY
│   ├── helpers.py            ← get_logger(), df_to_csv_bytes()
│   └── exporters.py          ← to_csv(), to_excel(), to_json(), to_parquet()
├── tests/
│   ├── test_ingestion.py
│   ├── test_cleaning.py
│   └── test_exploration.py
├── assets/
│   └── css/aura.css          ← Full design system (CSS variables, glassmorphism)
├── .env                      ← NEVER commit. Contains API keys.
├── .env.example              ← Safe to commit. Template with blank values.
├── .gitignore                ← Covers .env, .venv, __pycache__, poppler-*/
├── requirements.txt
└── README.md
```

---

## Session State Contract

All state lives in `state/session.py`. NEVER use raw `st.session_state["magic_string"]`.

```python
from state.session import get_session, reset_session

session = get_session()
session.raw_df        # pd.DataFrame | None — original uploaded file
session.cleaned_df    # pd.DataFrame | None — after cleaning pipeline
session.cleaning_log  # list[dict]  — each step: {step, affected_columns, detail}
session.profile       # dict        — exploration stats cache
session.chat_history  # list[dict]  — [{role, content}, ...] AI conversation
session.ocr_text      # str         — extracted PDF text
session.file_name     # str         — uploaded filename
session.file_size_kb  # float       — file size
```

---

## Engine Signatures (source of truth)

```python
# ingestion.py
def load_file(file) -> tuple[pd.DataFrame, dict]:
    # meta = {name, size_kb, n_rows, n_cols, format}

# cleaning.py
@dataclass
class CleaningConfig:
    rename_columns: bool = True
    normalize_strings: bool = True
    detect_dates: bool = True
    remove_empty_cols: bool = True
    fill_missing: bool = True
    drop_duplicates: bool = True

def clean_dataframe(df, config: CleaningConfig = CleaningConfig()) -> tuple[pd.DataFrame, list[dict]]:

# exploration.py
def get_basic_info(df) -> dict
def get_column_overview(df) -> pd.DataFrame
def get_numeric_summary(df) -> pd.DataFrame
def plot_histogram(df, column, bins=30) -> go.Figure
def plot_boxplot(df, column) -> go.Figure
def plot_correlation_heatmap(df) -> go.Figure
def plot_missing_heatmap(df) -> go.Figure
def plot_value_counts(df, column, top_n=20) -> go.Figure
def plot_timeseries(df, date_col, value_col) -> go.Figure

# ai_insights.py
class AIProvider(Enum):
    CLAUDE = "claude"
    OPENAI = "openai"

def ask_ai(df, question, provider: AIProvider, stream=True) -> Generator | str

QUICK_PROMPTS: list[str]  # 5 pre-built prompts

# audio_video.py
def transcribe_audio(audio_file_path, model_size="base") -> dict
def extract_audio_features(audio_file_path) -> dict
def extract_frames_from_video(video_file_path, n_frames=6) -> list[np.ndarray]

# exporters.py
def to_csv(df) -> bytes
def to_excel(df, sheet_name="AURA") -> bytes
def to_json(df, orient="records") -> bytes
def to_parquet(df) -> bytes
```

---

## Design System (CSS)

Design tokens in `assets/css/aura.css`:

| Token | Value |
|-------|-------|
| `--color-bg` | `#020617` |
| `--color-surface` | `rgba(15, 23, 42, 0.95)` |
| `--color-border-accent` | `rgba(124, 58, 237, 0.5)` |
| `--color-purple` | `#7C3AED` |
| `--color-blue` | `#3B82F6` |
| `--color-text` | `#F1F5F9` |
| `--color-text-muted` | `#94A3B8` |
| `--radius-md` | `14px` |
| `--shadow-card` | `0 4px 24px rgba(0,0,0,0.4)` |
| `--transition` | `200ms cubic-bezier(0.4, 0, 0.2, 1)` |

CSS classes: `.aura-header` `.aura-card` `.aura-metric-card` `.aura-feature-card`
`.aura-chat-user` `.aura-chat-assistant` `.aura-tag` `.aura-code`

Chart theme: `plotly_dark` template + transparent background + `#E2E8F0` font.
Apply `fig.update_layout(**CHART_THEME)` on every chart before returning.

---

## Coding Standards

- Every file starts with `from __future__ import annotations`
- Type hints on every function signature — no exceptions
- Docstring on every public function (one line minimum)
- Logger: `logger = get_logger(__name__)` from `utils.helpers`
- Never bare `except:` — always catch specific exception types
- No hardcoded session keys — use `state/session.py`
- Imports order: stdlib → third-party → local, blank line between groups
- Line length: 88 (Black default)
- No `print()` in production code — use logger
- All Streamlit pages must call `get_session()` at the top, not access st.session_state directly

---

## Environment Variables

Loaded via `utils/config.py` using `python-dotenv`.

| Variable | Required | Purpose |
|----------|----------|---------|
| `DEBUG` | No | Enable debug logging (0 or 1) |
| `POPPLER_PATH` | For OCR | Path to poppler bin folder |
| `OPENAI_API_KEY` | For OpenAI AI | sk-... |
| `ANTHROPIC_API_KEY` | For Claude AI | sk-ant-... |

**CRITICAL: `.env` is in `.gitignore`. Never commit it. Never log its values.**

---

## What NOT to Do

- Do NOT add `.env` to git — it has API keys
- Do NOT remove `.venv/` or `poppler-25.11.0/`
- Do NOT revert to single-file app.py with tabs — the multi-page architecture is intentional
- Do NOT use `st.session_state["raw_df"]` directly — use `get_session().raw_df`
- Do NOT use `WidthType.PERCENTAGE` in docx (breaks Google Docs)
- Do NOT add light mode — AURA is dark-only by design
- Do NOT skip `from __future__ import annotations` in new files
- Do NOT use unicode bullet characters manually — use proper list formatting

---

## Pending Work (V2 Build Phases)

### Phase 1 — GitHub-Ready Foundation ← NEXT
- [ ] Manual delete: `README/` folder, `requirements.txt.tmp`, empty `poppler/`
- [ ] Create `state/session.py`
- [ ] Create `utils/exporters.py`
- [ ] Refactor `app.py` as landing page (remove tab logic)
- [ ] Update `README.md` with screenshot + badges
- [ ] `git init` → first commit → push to GitHub

### Phase 2 — Core Feature Upgrade
- [ ] Add Plotly charts to `exploration.py`
- [ ] Build all 5 pages in `pages/`
- [ ] Multi-provider AI in `ai_insights.py` (Claude + OpenAI)
- [ ] `CleaningConfig` + cleaning log in `cleaning.py`
- [ ] Enhanced `ingestion.py` (multi-format, encoding detection)
- [ ] Full test suite in `tests/`

### Phase 3 — Advanced Features
- [ ] Implement `audio_video.py` (Whisper + librosa + OpenCV)
- [ ] Streaming AI responses
- [ ] Formatted Excel export (openpyxl styled headers)
- [ ] Deploy to Streamlit Community Cloud
- [ ] GitHub Actions CI (pytest + ruff)

### Phase 4 — UX Polish (after Phase 3)
- [ ] Full CSS design system rewrite
- [ ] Landing page animated hero
- [ ] Onboarding flow
- [ ] Progress indicators / skeleton loaders
- [ ] Mobile responsiveness

---

## Key Files Created by Cowork (do not delete)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | This file — project intelligence for Claude Code |
| `memory.md` | Personal workspace memory and decision log |
| `AURA_System_Design.docx` | Full V2 architecture document (6 sections) |
| `AURA_V2_MASTER_PROMPT.md` | Master prompt to paste into Antigravity agent |
| `.gitignore` | Git exclusions — covers .env, .venv, __pycache__, poppler-* |
| `.vscode/settings.json` | Python interpreter, Black formatter, pytest config |
| `.vscode/extensions.json` | Recommended extensions list |
| `.vscode/launch.json` | Run AURA + Run Tests launch configs |

---

## Git Workflow

```bash
# First push
git init
git add .
git commit -m "feat: AURA V1 — initial portfolio project"
git remote add origin https://github.com/SKAY/AURA.git
git push -u origin main

# Feature development
git checkout -b feat/v2-session-state
# ... build ...
git add .
git commit -m "feat: add centralised session state manager"
git push origin feat/v2-session-state
# → open PR → merge to main
```

Commit convention: `feat:` `fix:` `refactor:` `docs:` `test:` `style:` `chore:`
