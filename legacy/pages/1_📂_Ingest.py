"""AURA — Page 1: Data Ingestion."""
from __future__ import annotations

import streamlit as st

from engines.ingestion import load_file
from state.session import get_session
from utils.helpers import (
    cta_next,
    get_logger,
    load_css,
    metric_card,
    page_header,
    show_pipeline_progress,
    show_sidebar_status,
)

logger = get_logger(__name__)

st.set_page_config(page_title="AURA — Ingest", page_icon="📂", layout="wide")
load_css()
show_pipeline_progress(1)

with st.sidebar:
    show_sidebar_status()

page_header("📂", "Data Ingestion", "Upload and validate your dataset — CSV · Excel · JSON · Parquet · TSV")

sess = get_session()

# ── Upload zone ───────────────────────────────────────────────────────────────
st.markdown('<div class="aura-upload-zone">', unsafe_allow_html=True)
uploaded = st.file_uploader(
    "Drop your file here or click Browse",
    type=["csv", "xlsx", "xls", "json", "parquet", "tsv"],
    label_visibility="collapsed",
)
st.markdown(
    '<p style="color:#475569;font-size:0.78rem;margin-top:0.4rem;font-family:monospace;">'
    "Limit 200 MB per file · CSV · XLS · XLSX · JSON · PARQUET · TSV</p>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# ── After upload ──────────────────────────────────────────────────────────────
if uploaded is not None:
    try:
        df, meta = load_file(uploaded)
    except ValueError as exc:
        st.error(str(exc))
        logger.error("Ingestion error: %s", exc)
        df, meta = None, None

    if df is not None and meta is not None:
        sess.raw_df = df
        sess.file_name = meta["name"]
        sess.file_size_kb = meta["size_kb"]
        sess.cleaned_df = None
        sess.cleaning_log = []

        st.markdown("<br>", unsafe_allow_html=True)

        # Metrics row
        issues = int(df.isnull().sum().sum())
        m_cols = st.columns(5)
        metrics_data = [
            (f"{meta['n_rows']:,}", "Rows",    ""),
            (f"{meta['n_cols']}",   "Columns", ""),
            (f"{meta['size_kb']} KB", "Size",  "accent"),
            (meta["format"],        "Format",  ""),
            (
                f"{issues:,} missing" if issues else "Clean",
                "Issues",
                "warn" if issues else "success",
            ),
        ]
        for col, (val, label, variant) in zip(m_cols, metrics_data):
            with col:
                st.markdown(metric_card(val, label, variant), unsafe_allow_html=True)

        # Preview table
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<h3 style="color:#F1F5F9;font-size:1rem;font-weight:700;margin-bottom:0.7rem;">'
            'Preview <span style="color:#475569;font-weight:400;font-size:0.85rem;">— first 5 rows</span>'
            "</h3>",
            unsafe_allow_html=True,
        )
        preview = df.head(5)
        th_cells = "".join(f"<th>{c}</th>" for c in preview.columns)
        rows_html = ""
        for _, row in preview.iterrows():
            tds = ""
            for v in row:
                sv = str(v)
                if sv in ("nan", "None", "NaT", ""):
                    tds += '<td class="warn">—</td>'
                else:
                    # Truncate long values
                    display = sv if len(sv) <= 40 else sv[:37] + "…"
                    tds += f"<td>{display}</td>"
            rows_html += f"<tr>{tds}</tr>"

        st.markdown(
            f"""
<div style="overflow-x:auto;border-radius:12px;border:1px solid #1E2A50;">
<table class="aura-table">
  <thead><tr>{th_cells}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        cta_next("Next: Clean Data →", "pages/2_🧼_Clean.py", "Dataset validated — ready for cleaning.")

elif sess.raw_df is not None:
    # Already have data — show it
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        f"**{sess.file_name}** is already loaded "
        f"({sess.raw_df.shape[0]:,} rows · {sess.raw_df.shape[1]} cols). "
        "Upload a new file above to replace it."
    )
    preview = sess.raw_df.head(5)
    th_cells = "".join(f"<th>{c}</th>" for c in preview.columns)
    rows_html = ""
    for _, row in preview.iterrows():
        tds = "".join(
            f'<td class="warn">—</td>' if str(v) in ("nan", "None", "NaT", "")
            else f"<td>{str(v)[:40]}</td>"
            for v in row
        )
        rows_html += f"<tr>{tds}</tr>"
    st.markdown(
        f"""
<div style="overflow-x:auto;border-radius:12px;border:1px solid #1E2A50;margin-bottom:1rem;">
<table class="aura-table">
  <thead><tr>{th_cells}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>
</div>
""",
        unsafe_allow_html=True,
    )
    cta_next("Next: Clean Data →", "pages/2_🧼_Clean.py", "Dataset loaded — ready for cleaning.")

else:
    # Empty state
    st.markdown(
        """
<div style="text-align:center;padding:3rem 1rem;color:#475569;">
  <div style="font-size:2.5rem;margin-bottom:0.75rem;">👆</div>
  <p style="font-size:0.9rem;">Drop a file above to begin your analysis pipeline.</p>
  <p style="font-size:0.78rem;font-family:monospace;opacity:0.7;margin-top:0.3rem;">
    CSV &nbsp;·&nbsp; Excel &nbsp;·&nbsp; JSON &nbsp;·&nbsp; Parquet &nbsp;·&nbsp; TSV</p>
</div>
""",
        unsafe_allow_html=True,
    )
