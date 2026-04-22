"""AURA — Luminal Void | Landing Page."""
from __future__ import annotations

import streamlit as st
from utils.helpers import load_css, show_sidebar_status

st.set_page_config(
    page_title="AURA — Universal Data Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)
load_css()

with st.sidebar:
    show_sidebar_status()

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div style="text-align:center;padding:4.5rem 2rem 2.5rem;">
  <div style="display:inline-flex;align-items:center;justify-content:center;
              width:72px;height:72px;border-radius:18px;
              background:linear-gradient(135deg,#6C3FE5 0%,#3B82F6 100%);
              font-size:2rem;margin-bottom:1.4rem;
              box-shadow:0 8px 32px rgba(108,63,229,0.4);">⚡</div>
  <h1 style="color:#F1F5F9;font-size:2.6rem;font-weight:700;
             letter-spacing:-0.02em;margin:0 0 0.6rem;">AURA</h1>
  <p style="color:#94A3B8;font-size:1rem;max-width:480px;
            margin:0 auto 2.2rem;line-height:1.65;">
    Universal Data Engine — ingest, clean, explore, and query your data with AI.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Feature grid ─────────────────────────────────────────────────────────────
FEATURES = [
    ("📂", "Ingest", "CSV · Excel · JSON · Parquet · TSV", "pages/1_📂_Ingest.py", "Start: Upload Data →"),
    ("🧼", "Clean",  "Rename · Fill · Dedupe · Date detect", "pages/2_🧼_Clean.py", "Open Clean →"),
    ("🔍", "Explore","Charts · Correlation · Missing values",  "pages/3_🔍_Explore.py", "Open Explore →"),
    ("🤖", "AI Chat","Claude Sonnet · GPT-4o-mini",           "pages/4_🤖_AI_Chat.py", "Open AI Chat →"),
    ("📄", "Docs",   "OCR · Audio · Video frames · Export",   "pages/5_📄_Documents.py", "Open Docs →"),
]

col_a, col_b = st.columns(2, gap="large")
cols = [col_a, col_b, col_a, col_b, col_a]

for (icon, title, desc, page, cta_label), col in zip(FEATURES, cols):
    with col:
        st.markdown(
            f"""
<div class="aura-card" style="margin-bottom:1rem;">
  <div style="font-size:2rem;margin-bottom:0.6rem;">{icon}</div>
  <div style="font-size:1rem;font-weight:700;color:#F1F5F9;
              margin-bottom:0.3rem;">{title}</div>
  <div style="font-size:0.82rem;color:#475569;
              font-family:monospace;">{desc}</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.page_link(page, label=cta_label, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    "<p style='text-align:center;color:#1E2A50;font-size:0.78rem;"
    "margin-top:2.5rem;'>AURA v2.0 · Python 3.11 · Streamlit · Claude Sonnet 4.6</p>",
    unsafe_allow_html=True,
)
