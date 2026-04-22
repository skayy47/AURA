"""AURA — Page 4: AI Data Analyst chat."""
from __future__ import annotations

import streamlit as st

from engines.ai_insights import AIProvider, QUICK_PROMPTS, ask_ai
from state.session import get_session
from utils.helpers import (
    get_logger,
    load_css,
    page_header,
    require_dataset,
    show_pipeline_progress,
    show_sidebar_status,
)

logger = get_logger(__name__)

st.set_page_config(page_title="AURA — AI Chat", page_icon="🤖", layout="wide")
load_css()
show_pipeline_progress(4)

with st.sidebar:
    show_sidebar_status()

require_dataset(cleaned=True)

page_header("🤖", "AI Insights", "Ask anything about your dataset in plain English")

sess = get_session()
df = sess.cleaned_df

# ── Provider selector ─────────────────────────────────────────────────────────
provider_label = st.radio(
    "AI Provider",
    ["Claude Sonnet 4.6 (Anthropic)", "GPT-4o-mini (OpenAI)"],
    horizontal=True,
)
provider = AIProvider.CLAUDE if "Anthropic" in provider_label else AIProvider.OPENAI

# ── Quick prompts ─────────────────────────────────────────────────────────────
st.markdown(
    '<p style="font-size:0.82rem;font-weight:700;color:#94A3B8;'
    'text-transform:uppercase;letter-spacing:0.08em;margin:1rem 0 0.4rem;">'
    "Quick prompts</p>",
    unsafe_allow_html=True,
)
quick_cols = st.columns(len(QUICK_PROMPTS))
quick_question: str | None = None
for col, prompt in zip(quick_cols, QUICK_PROMPTS):
    with col:
        if st.button(prompt, use_container_width=True):
            quick_question = prompt

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in sess.chat_history:
    css_class = "aura-chat-user" if msg["role"] == "user" else "aura-chat-assistant"
    st.markdown(
        f'<div class="{css_class}">{msg["content"]}</div>',
        unsafe_allow_html=True,
    )

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask about your dataset…")
question = quick_question or (user_input or "").strip()

if question:
    sess.chat_history.append({"role": "user", "content": question})
    st.markdown(
        f'<div class="aura-chat-user">{question}</div>',
        unsafe_allow_html=True,
    )
    try:
        response_placeholder = st.empty()
        full_response = ""
        with st.spinner("Thinking…"):
            for chunk in ask_ai(df, question, provider, stream=True):
                full_response += chunk
                response_placeholder.markdown(full_response)
        sess.chat_history.append({"role": "assistant", "content": full_response})
    except ValueError as exc:
        st.markdown(
            f"""
<div class="aura-card-elevated" style="border-color:rgba(239,68,68,0.4);">
  <strong style="color:#EF4444;">⚠ API key not configured</strong><br/>
  <code style="font-size:0.82rem;color:#94A3B8;">{exc}</code>
</div>
""",
            unsafe_allow_html=True,
        )
    except Exception as exc:
        logger.exception("AI chat error: %s", exc)
        st.error(f"Unexpected error: {exc}")

# ── Clear conversation ────────────────────────────────────────────────────────
if sess.chat_history and st.button("🗑  Clear conversation"):
    sess.chat_history = []
    st.rerun()

# ── CTA ───────────────────────────────────────────────────────────────────────
st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
st.page_link("pages/5_📄_Documents.py", label="Next: Docs & Export →", use_container_width=True)
