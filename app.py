"""AURA V2 — Landing / Home page."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from state.session import get_session, reset_session
from utils.config import is_debug_mode
from utils.helpers import show_sidebar_status

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="AURA – Universal Data Engine",
    page_icon="⚡",
    layout="wide",
)


# -------------------------------------------------
# CSS
# -------------------------------------------------
def inject_css() -> None:
    """Inject the AURA design-system stylesheet."""
    css_path = Path("assets/css/aura.css")
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


inject_css()

# -------------------------------------------------
# Sidebar — delegated to shared helper
# -------------------------------------------------
show_sidebar_status()

# -------------------------------------------------
# Hero header
# -------------------------------------------------
st.markdown(
    """
<div class="aura-hero">
  <div class="aura-hero-logo">⚡</div>
  <div>
    <h1 class="aura-hero-title">AURA</h1>
    <p class="aura-hero-subtitle">
      Universal engine for data ingestion, cleaning, exploration — and AI insights.
    </p>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Active dataset banner
# -------------------------------------------------
session = get_session()
if session.raw_df is not None:
    cleaned_note = (
        f" · ✅ cleaned ({session.cleaned_df.shape[0]:,} rows)"
        if session.cleaned_df is not None
        else " · not cleaned yet"
    )
    st.success(
        f"**{session.file_name}** · {session.raw_df.shape[0]:,} rows · "
        f"{session.file_size_kb:.1f} KB{cleaned_note}"
    )

# -------------------------------------------------
# Section heading
# -------------------------------------------------
st.markdown(
    '<h2 class="section-heading">Where would you like to start?</h2>',
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Feature cards — 2-column grid
# -------------------------------------------------
FEATURES = [
    {
        "icon": "📂",
        "title": "Ingest",
        "tag": "Step 1",
        "desc": "Upload CSV, Excel, JSON, Parquet or TSV. Auto-detects encoding and multi-sheet workbooks.",
        "page": "pages/1_📂_Ingest.py",
        "label": "Open Ingest →",
    },
    {
        "icon": "🧼",
        "title": "Clean",
        "tag": "Step 2",
        "desc": "Rename columns, fill missing values, drop duplicates, auto-detect dates — all configurable.",
        "page": "pages/2_🧼_Clean.py",
        "label": "Open Clean →",
    },
    {
        "icon": "🔍",
        "title": "Explore",
        "tag": "Step 3",
        "desc": "Interactive Plotly charts — histograms, box plots, correlation heatmaps, value counts.",
        "page": "pages/3_🔍_Explore.py",
        "label": "Open Explore →",
    },
    {
        "icon": "🤖",
        "title": "AI Chat",
        "tag": "Step 4",
        "desc": "Ask Claude Sonnet 4.6 or GPT-4o-mini questions about your data in plain English.",
        "page": "pages/4_🤖_AI_Chat.py",
        "label": "Open AI Chat →",
    },
    {
        "icon": "📄",
        "title": "Documents",
        "tag": "Extra",
        "desc": "OCR text from PDFs via Tesseract. Transcribe audio with Whisper. Extract video frames.",
        "page": "pages/5_📄_Documents.py",
        "label": "Open Documents →",
    },
]

col_a, col_b = st.columns(2)
cols = [col_a, col_b, col_a, col_b, col_a]

for feature, col in zip(FEATURES, cols):
    with col:
        st.markdown(
            f"""
<div class="aura-feature-card">
  <div class="feature-card-top">
    <span class="feature-card-icon">{feature["icon"]}</span>
    <span class="feature-card-tag">{feature["tag"]}</span>
  </div>
  <h3 class="feature-card-title">{feature["title"]}</h3>
  <p class="feature-card-desc">{feature["desc"]}</p>
</div>
""",
            unsafe_allow_html=True,
        )
        st.page_link(feature["page"], label=feature["label"], use_container_width=True)
