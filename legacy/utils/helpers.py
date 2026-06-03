from __future__ import annotations

import logging
from pathlib import Path

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


def load_css() -> None:
    """Inject AURA Luminal Void design system CSS."""
    css_path = Path(__file__).parent.parent / "assets" / "css" / "aura.css"
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


def page_header(icon: str, title: str, subtitle: str = "") -> None:
    """Render the standard AURA Luminal Void page header."""
    sub_html = f'<p class="aura-page-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
<div class="aura-page-header">
  <div class="aura-page-icon">{icon}</div>
  <div>
    <h1 class="aura-page-title">{title}</h1>
    {sub_html}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


# Keep legacy alias so engine files that import show_page_header still work
show_page_header = page_header


def show_pipeline_progress(current: int) -> None:
    """
    Render the 5-step pipeline bar pinned to top of page content.
    current: 1=Ingest · 2=Clean · 3=Explore · 4=AI Chat · 5=Docs
    """
    steps = [
        ("📂", "Ingest"),
        ("🧼", "Clean"),
        ("🔍", "Explore"),
        ("🤖", "AI Chat"),
        ("📄", "Docs"),
    ]
    html_steps = ""
    for i, (icon, label) in enumerate(steps, 1):
        if i == current:
            cls = "aura-step active"
            sub = '<div class="aura-step-sub">In progress</div>'
        elif i < current:
            cls = "aura-step done"
            sub = '<div class="aura-step-sub">✓ Done</div>'
        else:
            cls = "aura-step"
            sub = ""
        html_steps += f"""
        <div class="{cls}">
          <div class="aura-step-label">{icon}&nbsp;&nbsp;{label}</div>
          {sub}
        </div>"""
    st.markdown(
        f'<div class="aura-pipeline">{html_steps}</div>',
        unsafe_allow_html=True,
    )


def show_sidebar_status() -> None:
    """Render sidebar brand, navigation links, and live dataset status."""
    from state.session import get_session, reset_session

    sess = get_session()

    # Brand block
    st.sidebar.markdown(
        """
<div style="padding:20px 16px 12px;border-bottom:1px solid #1E2A50;margin-bottom:4px;">
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="background:#6C3FE5;border-radius:10px;width:40px;height:40px;
                display:flex;align-items:center;justify-content:center;
                font-size:1.3rem;flex-shrink:0;">⚡</div>
    <div>
      <div style="font-size:1.05rem;font-weight:700;color:#F1F5F9;
                  letter-spacing:0.04em;">AURA</div>
      <div style="font-size:0.7rem;color:#475569;letter-spacing:0.06em;">
        data engine</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Nav links
    st.sidebar.page_link("app.py",                   label="🏠  Home")
    st.sidebar.page_link("pages/1_📂_Ingest.py",     label="📂  Ingest")
    st.sidebar.page_link("pages/2_🧼_Clean.py",      label="🧼  Clean")
    st.sidebar.page_link("pages/3_🔍_Explore.py",    label="🔍  Explore")
    st.sidebar.page_link("pages/4_🤖_AI_Chat.py",    label="🤖  AI Chat")
    st.sidebar.page_link("pages/5_📄_Documents.py",  label="📄  Docs")

    # Dataset status card
    st.sidebar.markdown(
        '<div style="height:1px;background:#1E2A50;margin:10px 0;"></div>',
        unsafe_allow_html=True,
    )

    if sess.raw_df is not None:
        rows, cols = sess.raw_df.shape
        fname = sess.file_name or "dataset"
        if sess.cleaned_df is not None:
            badge_color = "#10B981"
            badge_text = "✓ Cleaned"
        else:
            badge_color = "#F59E0B"
            badge_text = "⚠ Not cleaned"

        st.sidebar.markdown(
            f"""
<div style="background:#0E162E;border:1px solid #1E2A50;border-radius:10px;
            padding:12px 14px;margin:4px 8px 8px 8px;">
  <div style="font-family:monospace;font-size:0.8rem;color:#F1F5F9;
              white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
       title="{fname}">{fname}</div>
  <div style="font-size:0.76rem;color:#8B5CF6;margin-top:4px;">
    {rows:,} rows · {cols} cols
  </div>
  <span style="display:inline-block;margin-top:6px;padding:2px 10px;
               border-radius:999px;font-size:0.7rem;font-weight:600;
               background:rgba(16,185,129,0.12);color:{badge_color};">
    {badge_text}
  </span>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            '<p style="font-size:0.8rem;color:#475569;padding:4px 16px;'
            'font-style:italic;">No dataset loaded yet.</p>',
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        '<div style="height:1px;background:#1E2A50;margin:4px 0 10px 0;"></div>',
        unsafe_allow_html=True,
    )
    if st.sidebar.button("⟳  New Dataset", use_container_width=True):
        reset_session()
        st.rerun()


def require_dataset(cleaned: bool = False) -> bool:
    """
    Stop page render with a polished empty state when required data is missing.
    Returns True when data is present, never returns False (calls st.stop()).
    """
    from state.session import get_session

    sess = get_session()
    df = sess.cleaned_df if cleaned else sess.raw_df

    if df is not None:
        return True

    if cleaned:
        icon = "🧼"
        title = "No cleaned dataset"
        desc = "Run the Clean step first before continuing."
        link = "pages/2_🧼_Clean.py"
        cta = "Go to Clean →"
    else:
        icon = "📂"
        title = "No dataset loaded"
        desc = "Upload a CSV, Excel, JSON, Parquet, or TSV file to begin."
        link = "pages/1_📂_Ingest.py"
        cta = "Upload a dataset →"

    st.markdown(
        f"""
<div style="background:#0E162E;border:1px solid rgba(90,60,200,0.4);
            border-radius:16px;padding:3rem 2rem;text-align:center;
            max-width:460px;margin:3rem auto;">
  <div style="font-size:2.8rem;margin-bottom:1rem;">{icon}</div>
  <div style="color:#F1F5F9;font-weight:700;font-size:1.2rem;
              margin-bottom:0.5rem;">{title}</div>
  <div style="color:#94A3B8;font-size:0.88rem;line-height:1.6;">{desc}</div>
</div>
""",
        unsafe_allow_html=True,
    )
    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.page_link(link, label=cta, use_container_width=True)
    st.stop()
    return False  # unreachable — satisfies type checker


def metric_card(value: str, label: str, variant: str = "") -> str:
    """Return HTML for a single Luminal Void metric card."""
    cls = f"aura-metric-val {variant}".strip()
    return f"""
<div class="aura-metric">
  <div class="aura-metric-label">{label}</div>
  <div class="{cls}">{value}</div>
</div>"""


def cta_next(label: str, page: str, status_text: str = "") -> None:
    """Render a bottom CTA row: optional status text + styled page_link button."""
    st.markdown('<div class="aura-cta-row">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        if status_text:
            st.markdown(
                f'<p class="aura-cta-label">{status_text}</p>',
                unsafe_allow_html=True,
            )
    with col2:
        st.page_link(page, label=label, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
