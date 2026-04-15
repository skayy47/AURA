from __future__ import annotations

import logging
from io import BytesIO

import pandas as pd
import streamlit as st


_LOGGER_CACHE: dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """Central logger factory with simple console formatting."""
    if name in _LOGGER_CACHE:
        return _LOGGER_CACHE[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    _LOGGER_CACHE[name] = logger
    return logger


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to CSV bytes for Streamlit download buttons."""
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()


# -----------------------------------------------------------------
# Page header
# -----------------------------------------------------------------

def show_page_header(icon: str, title: str, subtitle: str) -> None:
    """Render a consistent page header with icon, title, and subtitle."""
    st.markdown(
        f"""
<div class="aura-page-header">
  <div class="page-header-icon">{icon}</div>
  <div>
    <h1 class="page-header-title">{title}</h1>
    <p class="page-header-subtitle">{subtitle}</p>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------
# Pipeline progress breadcrumb
# -----------------------------------------------------------------

def show_pipeline_progress(current_step: int) -> None:
    """
    Render a 5-step pipeline breadcrumb.
    current_step: 1=Ingest  2=Clean  3=Explore  4=AI Chat  5=Documents
    """
    steps = [
        ("📂", "Ingest"),
        ("🧼", "Clean"),
        ("🔍", "Explore"),
        ("🤖", "AI Chat"),
        ("📄", "Docs"),
    ]
    cols = st.columns(len(steps))
    for i, (col, (emoji, label)) in enumerate(zip(cols, steps), 1):
        with col:
            if i < current_step:
                st.markdown(
                    f'<div class="step-done">{emoji} {label} ✓</div>',
                    unsafe_allow_html=True,
                )
            elif i == current_step:
                st.markdown(
                    f'<div class="step-active">{emoji} {label}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="step-pending">{emoji} {label}</div>',
                    unsafe_allow_html=True,
                )
    st.markdown('<div style="margin-bottom:1.5rem;"></div>', unsafe_allow_html=True)


# -----------------------------------------------------------------
# Sidebar — brand + nav + dataset status (used on every page)
# -----------------------------------------------------------------

def show_sidebar_status() -> None:
    """Render the full sidebar: brand, navigation, dataset status, reset button."""
    from state.session import get_session, reset_session

    session = get_session()

    # Brand
    st.sidebar.markdown(
        """
<div class="sidebar-brand">
  <span class="sidebar-brand-icon">⚡</span>
  <span class="sidebar-brand-name">AURA</span>
</div>
""",
        unsafe_allow_html=True,
    )

    # Navigation
    st.sidebar.page_link("app.py",                    label="🏠  Home")
    st.sidebar.page_link("pages/1_📂_Ingest.py",     label="📂  Ingest")
    st.sidebar.page_link("pages/2_🧼_Clean.py",      label="🧼  Clean")
    st.sidebar.page_link("pages/3_🔍_Explore.py",    label="🔍  Explore")
    st.sidebar.page_link("pages/4_🤖_AI_Chat.py",    label="🤖  AI Chat")
    st.sidebar.page_link("pages/5_📄_Documents.py",  label="📄  Documents")

    # Dataset status
    st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    if session.raw_df is not None:
        cleaned_badge = (
            f'<span class="sidebar-badge sidebar-badge-green">'
            f'✓ cleaned · {session.cleaned_df.shape[0]:,} rows</span>'
            if session.cleaned_df is not None
            else '<span class="sidebar-badge sidebar-badge-amber">not cleaned yet</span>'
        )
        st.sidebar.markdown(
            f"""
<div class="sidebar-dataset-card">
  <div class="sidebar-dataset-name">{session.file_name}</div>
  <div class="sidebar-dataset-meta">
    {session.raw_df.shape[0]:,} rows &nbsp;·&nbsp;
    {session.raw_df.shape[1]} cols &nbsp;·&nbsp;
    {session.file_size_kb:.1f} KB
  </div>
  {cleaned_badge}
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            '<p class="sidebar-no-data">No dataset loaded yet.</p>',
            unsafe_allow_html=True,
        )

    st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    if st.sidebar.button("⟳  New Dataset", use_container_width=True):
        reset_session()
        st.rerun()


# -----------------------------------------------------------------
# Dataset guard — polished empty state
# -----------------------------------------------------------------

def require_dataset(cleaned: bool = False) -> bool:
    """
    Stop the page with a polished empty state if required data is absent.
    Returns True when data is present so callers can assert it.
    """
    from state.session import get_session

    session = get_session()

    df = session.cleaned_df if cleaned else session.raw_df
    if df is not None:
        return True

    if cleaned:
        icon   = "🔍"
        title  = "No cleaned dataset yet"
        desc   = "Run the cleaning pipeline before exploring or chatting with AI."
        link   = "pages/2_🧼_Clean.py"
        cta    = "Go to Clean →"
    else:
        icon   = "📂"
        title  = "No dataset loaded"
        desc   = "Upload a CSV, Excel, JSON, Parquet, or TSV file to get started."
        link   = "pages/1_📂_Ingest.py"
        cta    = "Upload a dataset →"

    st.markdown(
        f"""
<div class="aura-empty-state">
  <div class="empty-icon">{icon}</div>
  <h2 class="empty-title">{title}</h2>
  <p class="empty-desc">{desc}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.page_link(link, label=cta, use_container_width=True)

    st.stop()
    return False  # never reached, satisfies type checker
