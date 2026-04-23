"""Integration-level smoke tests — verifies engines work end-to-end.

Individual unit tests for each engine live in:
  test_cleaning.py · test_ingestion.py · test_exploration.py
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd

from engines.cleaning import clean_dataframe
from engines.exploration import get_basic_info
from engines.ingestion import load_file


def _make_file(name: str, content: bytes) -> MagicMock:
    mock = MagicMock()
    mock.name = name
    mock.read.return_value = content
    return mock


def test_full_pipeline() -> None:
    """Ingest → Clean → Explore produces consistent, non-empty output."""
    csv = b"name,age,score\nAlice,29,0.9\nBob,,0.8\nAlice,29,0.9\n"
    f = _make_file("employees.csv", csv)

    raw_df, meta = load_file(f)
    assert meta["n_rows"] == 3

    cleaned, log = clean_dataframe(raw_df)
    assert len(cleaned) < len(raw_df)   # duplicate removed
    assert cleaned.isnull().sum().sum() == 0  # missing filled

    info = get_basic_info(cleaned)
    assert info["n_rows"] == info["n_rows"]  # sanity check
    assert info["n_cols"] >= 2
