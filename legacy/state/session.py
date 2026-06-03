"""
Central session state manager for AURA.
All st.session_state keys are defined here — no magic strings anywhere else.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
import streamlit as st


@dataclass
class AuraSession:
    """Holds all runtime state for the AURA application."""

    # Raw upload
    raw_df: Optional[pd.DataFrame] = None
    file_name: str = ""
    file_size_kb: float = 0.0

    # After cleaning
    cleaned_df: Optional[pd.DataFrame] = None
    cleaning_log: list[dict] = field(default_factory=list)

    # After profiling
    profile: dict = field(default_factory=dict)

    # AI chat history: list of {"role": "user"|"assistant", "content": str}
    chat_history: list[dict] = field(default_factory=list)

    # OCR result
    ocr_text: str = ""


SESSION_KEY = "_aura_session"


def get_session() -> AuraSession:
    """Return the current AuraSession, creating it if absent."""
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = AuraSession()
    return st.session_state[SESSION_KEY]  # type: ignore[return-value]


def reset_session() -> None:
    """Wipe all session state and start fresh."""
    st.session_state[SESSION_KEY] = AuraSession()
