"""AURA — Page 4: AI Data Analyst chat."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from engines.ai_insights import AIProvider, QUICK_PROMPTS, ask_ai
from state.session import get_session
from utils.helpers import (
    get_logger,
    require_dataset,
    show_page_header,
    show_pipeline_progress,
    show_sidebar_status,
)

logger = get_logger(__name__)

st.set_page_config(page_title="AURA · AI Chat", page_icon="🤖", layout="wide")


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
show_pipeline_progress(4)
show_page_header("🤖", "AI Data Analyst", "Ask questions about your data in plain English")

require_dataset(cleaned=True)

df = session.cleaned_df

# -----------------------------------------------------------------
# Provider selector
# -----------------------------------------------------------------
provider_label = st.radio(
    "AI Provider",
    ["Claude Sonnet 4.6 (Anthropic)", "GPT-4o-mini (OpenAI)"],
    horizontal=True,
)
provider = (
    AIProvider.CLAUDE if "Anthropic" in provider_label else AIProvider.OPENAI
)

# -----------------------------------------------------------------
# Quick prompts
# -----------------------------------------------------------------
st.markdown("#### Quick prompts")
quick_cols = st.columns(len(QUICK_PROMPTS))
quick_question: str | None = None
for col, prompt in zip(quick_cols, QUICK_PROMPTS):
    with col:
        if st.button(prompt, use_container_width=True):
            quick_question = prompt

# -----------------------------------------------------------------
# Chat history display
# -----------------------------------------------------------------
for msg in session.chat_history:
    css_class = "aura-chat-user" if msg["role"] == "user" else "aura-chat-assistant"
    align = "right" if msg["role"] == "user" else "left"
    st.markdown(
        f'<div class="{css_class}" style="text-align:{align};margin:0.5rem 0;">'
        f'{msg["content"]}</div>',
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------
# Chat input
# -----------------------------------------------------------------
user_input = st.chat_input("Ask about your dataset…")
question = quick_question or (user_input or "").strip()

if question:
    session.chat_history.append({"role": "user", "content": question})
    st.markdown(
        f'<div class="aura-chat-user" style="text-align:right;margin:0.5rem 0;">'
        f"{question}</div>",
        unsafe_allow_html=True,
    )

    try:
        response_placeholder = st.empty()
        full_response = ""
        with st.spinner("Thinking…"):
            for chunk in ask_ai(df, question, provider, stream=True):
                full_response += chunk
                response_placeholder.markdown(full_response)
        session.chat_history.append({"role": "assistant", "content": full_response})
    except ValueError as exc:
        st.markdown(
            f"""
<div class="aura-card" style="border-color:var(--color-error);">
  <strong>⚠️ API key not configured</strong><br/>
  <code>{exc}</code>
</div>
""",
            unsafe_allow_html=True,
        )
    except Exception as exc:
        logger.exception("AI chat error: %s", exc)
        st.error(f"Unexpected error: {exc}")

# -----------------------------------------------------------------
# Clear conversation
# -----------------------------------------------------------------
if session.chat_history and st.button("🗑  Clear conversation"):
    session.chat_history = []
    st.rerun()

# -----------------------------------------------------------------
# Next step
# -----------------------------------------------------------------
st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
st.page_link(
    "pages/5_📄_Documents.py",
    label="Next: Process documents 📄 →",
    use_container_width=True,
)
