"""AURA — Page 2: Data Cleaning."""
from __future__ import annotations

import streamlit as st

from engines.cleaning import CleaningConfig, clean_dataframe
from state.session import get_session
from utils.exporters import to_csv, to_excel, to_json, to_parquet
from utils.helpers import (
    cta_next,
    get_logger,
    load_css,
    page_header,
    require_dataset,
    show_pipeline_progress,
    show_sidebar_status,
)

logger = get_logger(__name__)

st.set_page_config(page_title="AURA — Clean", page_icon="🧼", layout="wide")
load_css()
show_pipeline_progress(2)

with st.sidebar:
    show_sidebar_status()

require_dataset(cleaned=False)

page_header("🧼", "Data Cleaning", "Detect and fix quality issues automatically")

sess = get_session()

# ── Config panel ──────────────────────────────────────────────────────────────
with st.expander("⚙️  Cleaning Options", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        rename   = st.checkbox("Rename columns to snake_case", value=True)
        strings  = st.checkbox("Normalise string whitespace",  value=True)
    with col2:
        dates      = st.checkbox("Auto-detect date columns",    value=True)
        empty_cols = st.checkbox("Remove fully-empty columns",  value=True)
    with col3:
        fill  = st.checkbox("Fill missing values",  value=True)
        dupes = st.checkbox("Drop duplicate rows",  value=True)

if st.button("🧼  Run Cleaning Pipeline", type="primary"):
    config = CleaningConfig(
        rename_columns=rename,
        normalize_strings=strings,
        detect_dates=dates,
        remove_empty_cols=empty_cols,
        fill_missing=fill,
        drop_duplicates=dupes,
    )
    with st.spinner("Cleaning…"):
        cleaned_df, log = clean_dataframe(sess.raw_df, config)
    sess.cleaned_df = cleaned_df
    sess.cleaning_log = log
    st.success(f"✓ Cleaned — {len(log)} operations applied")

# ── Cleaning log ──────────────────────────────────────────────────────────────
if sess.cleaning_log:
    st.markdown(
        '<h3 style="color:#F1F5F9;font-size:0.95rem;font-weight:700;'
        'margin:1.2rem 0 0.6rem;">Cleaning Log</h3>',
        unsafe_allow_html=True,
    )
    for entry in sess.cleaning_log:
        step     = entry.get("step", "")
        detail   = entry.get("detail", "")
        affected = entry.get("affected_columns", [])
        cols_str = (", ".join(affected[:5]) + ("…" if len(affected) > 5 else "")) if affected else ""
        suffix   = f" <span style='color:#475569;'>({cols_str})</span>" if cols_str else ""
        st.markdown(
            f'<div style="color:#10B981;font-size:0.83rem;font-family:monospace;'
            f'padding:3px 0;">▸ {step}: {detail}{suffix}</div>',
            unsafe_allow_html=True,
        )

# ── Side-by-side diff + downloads ─────────────────────────────────────────────
if sess.cleaned_df is not None:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            '<p style="font-size:0.82rem;color:#94A3B8;font-weight:600;'
            'margin-bottom:0.4rem;">Before — raw (first 10 rows)</p>',
            unsafe_allow_html=True,
        )
        st.dataframe(sess.raw_df.head(10), use_container_width=True)
    with c2:
        st.markdown(
            '<p style="font-size:0.82rem;color:#10B981;font-weight:600;'
            'margin-bottom:0.4rem;">After — cleaned (first 10 rows)</p>',
            unsafe_allow_html=True,
        )
        st.dataframe(sess.cleaned_df.head(10), use_container_width=True)

    st.markdown(
        '<h3 style="color:#F1F5F9;font-size:0.95rem;font-weight:700;'
        'margin:1.2rem 0 0.6rem;">⬇ Download Cleaned Data</h3>',
        unsafe_allow_html=True,
    )
    dl1, dl2, dl3, dl4 = st.columns(4)
    with dl1:
        st.download_button("CSV",     data=to_csv(sess.cleaned_df),     file_name="aura_cleaned.csv",     mime="text/csv")
    with dl2:
        st.download_button("Excel",   data=to_excel(sess.cleaned_df),   file_name="aura_cleaned.xlsx",    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with dl3:
        st.download_button("JSON",    data=to_json(sess.cleaned_df),    file_name="aura_cleaned.json",    mime="application/json")
    with dl4:
        st.download_button("Parquet", data=to_parquet(sess.cleaned_df), file_name="aura_cleaned.parquet", mime="application/octet-stream")

    cta_next(
        "Next: Explore →",
        "pages/3_🔍_Explore.py",
        f"Cleaning complete — {sess.cleaned_df.shape[0]:,} rows · {sess.cleaned_df.shape[1]} columns.",
    )
