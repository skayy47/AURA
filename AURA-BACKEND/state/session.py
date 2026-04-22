"""
FastAPI backend session state manager.
Note: Streamlit session management is NOT used in the FastAPI backend.
See api/deps.py for the actual session store (in-memory dict with UUID keys).
This module is deprecated and kept for backwards compatibility only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd


@dataclass
class AuraSession:
    """(Deprecated) Streamlit-based session holder. Not used in FastAPI backend."""

    raw_df: Optional[pd.DataFrame] = None
    file_name: str = ""
    file_size_kb: float = 0.0
    cleaned_df: Optional[pd.DataFrame] = None
    cleaning_log: list[dict] = field(default_factory=list)
    profile: dict = field(default_factory=dict)
    chat_history: list[dict] = field(default_factory=list)
    ocr_text: str = ""
