"""AURA — Page 2: Data Cleaning."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from engines.cleaning import CleaningConfig, clean_dataframe
from state.session import get_session
from utils.exporters import to_csv, to_excel, to_json, to_parquet
from utils.helpers import (
    get_logger,
    require_dataset,
    show_page_header,
    show_pipeline_progress,
    show_sidebar_status,
)

logger = get_logger(__name__)

st.set_page_config(page_title="AURA · Clean", page_icon="🧼", layout="wide")


def inject_css() -> None:
    css_path = Path("assets/css/aura.css")
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


inject_css()

session = get_session()
show_sidebar_status()
show_pipeline_progress(2)
show_page_header("🧼", "Data Cleaning", "Configure and run the cleaning pipeline")

require_dataset(cleaned=False)

# -----------------------------------------------------------------
# Sidebar — cleaning config
# -----------------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown("#### 🛠 Cleaning options")
    config = CleaningConfig(
        rename_columns=st.checkbox("Rename columns to snake_case", value=True),
        normalize_strings=st.checkbox("Normalise string whitespace", value=True),
        detect_dates=st.checkbox("Auto-detect date columns", value=True),
        remove_empty_cols=st.checkbox("Remove fully-empty columns", value=True),
        fill_missing=st.checkbox("Fill missing values", value=True),
        drop_duplicates=st.checkbox("Drop duplicate rows", value=True),
    )

run = st.button("▶  Run cleaning", type="primary", use_container_width=True)

if run:
    with st.spinner("Cleaning…"):
        cleaned, log = clean_dataframe(session.raw_df, config)
    session.cleaned_df = cleaned
    session.cleaning_log = log

# -----------------------------------------------------------------
# Cleaning log
# -----------------------------------------------------------------
if session.cleaning_log:
    st.markdown("#### Cleaning log")
    log_df = pd.DataFrame(session.cleaning_log)
    log_df["affected_columns"] = log_df["affected_columns"].apply(
        lambda x: ", ".join(x) if x else "—"
    )
    log_df["status"] = "✅"
    log_df.columns = ["Step", "Columns affected", "Detail", "Status"]
    st.dataframe(log_df, use_container_width=True)

# -----------------------------------------------------------------
# Side-by-side preview + downloads
# -----------------------------------------------------------------
if session.cleaned_df is not None:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Before — raw (first 10 rows)**")
        st.dataframe(session.raw_df.head(10), use_container_width=True)
    with c2:
        st.markdown("**After — cleaned (first 10 rows)**")
        st.dataframe(session.cleaned_df.head(10), use_container_width=True)

    st.markdown("#### ⬇️ Download cleaned data")
    dl1, dl2, dl3, dl4 = st.columns(4)
    with dl1:
        st.download_button(
            "CSV",
            data=to_csv(session.cleaned_df),
            file_name="aura_cleaned.csv",
            mime="text/csv",
        )
    with dl2:
        st.download_button(
            "Excel",
            data=to_excel(session.cleaned_df),
            file_name="aura_cleaned.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with dl3:
        st.download_button(
            "JSON",
            data=to_json(session.cleaned_df),
            file_name="aura_cleaned.json",
            mime="application/json",
        )
    with dl4:
        st.download_button(
            "Parquet",
            data=to_parquet(session.cleaned_df),
            file_name="aura_cleaned.parquet",
            mime="application/octet-stream",
        )

    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
    st.success(
        f"✅ Cleaning complete — {session.cleaned_df.shape[0]:,} rows · "
        f"{session.cleaned_df.shape[1]} columns remaining."
    )
    st.page_link(
        "pages/3_🔍_Explore.py",
        label="Next: Explore your data 🔍 →",
        use_container_width=True,
    )
