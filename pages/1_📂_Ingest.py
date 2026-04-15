"""AURA — Page 1: Data Ingestion."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from engines.ingestion import load_file
from state.session import get_session
from utils.helpers import get_logger, show_page_header, show_pipeline_progress, show_sidebar_status

logger = get_logger(__name__)

st.set_page_config(page_title="AURA · Ingest", page_icon="📂", layout="wide")


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
show_pipeline_progress(1)
show_page_header("📂", "Data Ingestion", "Upload and validate your dataset")

# -----------------------------------------------------------------
uploaded = st.file_uploader(
    "Drop a file — CSV, Excel (.xls/.xlsx), JSON, Parquet, or TSV",
    type=["csv", "xls", "xlsx", "json", "parquet", "tsv"],
)

if uploaded is not None:
    try:
        df, meta = load_file(uploaded)
    except ValueError as exc:
        st.error(str(exc))
        logger.error("Ingestion error: %s", exc)
        df, meta = None, None

    if df is not None and meta is not None:
        session.raw_df = df
        session.file_name = meta["name"]
        session.file_size_kb = meta["size_kb"]
        session.cleaned_df = None
        session.cleaning_log = []

        # File summary card
        st.markdown(
            f"""
<div class="aura-card" style="margin-top:1.25rem;">
  <div class="ingest-success-row">
    <div class="ingest-success-icon">✅</div>
    <div>
      <div class="ingest-success-title">File loaded successfully</div>
      <div class="ingest-meta-grid">
        <div class="ingest-meta-item">
          <span class="ingest-meta-label">File</span>
          <span class="ingest-meta-value">{meta["name"]}</span>
        </div>
        <div class="ingest-meta-item">
          <span class="ingest-meta-label">Format</span>
          <span class="ingest-meta-value">{meta["format"]}</span>
        </div>
        <div class="ingest-meta-item">
          <span class="ingest-meta-label">Rows</span>
          <span class="ingest-meta-value">{meta["n_rows"]:,}</span>
        </div>
        <div class="ingest-meta-item">
          <span class="ingest-meta-label">Columns</span>
          <span class="ingest-meta-value">{meta["n_cols"]}</span>
        </div>
        <div class="ingest-meta-item">
          <span class="ingest-meta-label">Size</span>
          <span class="ingest-meta-value">{meta["size_kb"]} KB</span>
        </div>
      </div>
    </div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("#### Preview — first 10 rows")
        st.dataframe(df.head(10), use_container_width=True)

        st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
        st.success("✅ Dataset loaded — ready to clean.")
        st.page_link(
            "pages/2_🧼_Clean.py",
            label="Next: Clean your data 🧼 →",
            use_container_width=True,
        )

elif session.raw_df is not None:
    st.info(
        f"**{session.file_name}** is already loaded "
        f"({session.raw_df.shape[0]:,} rows · {session.raw_df.shape[1]} cols). "
        "Upload a new file above to replace it."
    )
    st.dataframe(session.raw_df.head(10), use_container_width=True)
    st.success("✅ Dataset loaded — ready to clean.")
    st.page_link(
        "pages/2_🧼_Clean.py",
        label="Next: Clean your data 🧼 →",
        use_container_width=True,
    )
else:
    st.markdown(
        """
<div class="aura-upload-hint">
  <div class="upload-hint-icon">👆</div>
  <p>Drop a file above to begin your analysis pipeline.</p>
  <p class="upload-hint-formats">CSV &nbsp;·&nbsp; Excel &nbsp;·&nbsp; JSON &nbsp;·&nbsp; Parquet &nbsp;·&nbsp; TSV</p>
</div>
""",
        unsafe_allow_html=True,
    )
