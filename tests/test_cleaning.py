"""Tests for engines/cleaning.py."""
from __future__ import annotations

import numpy as np
import pandas as pd

from engines.cleaning import CleaningConfig, clean_dataframe


def _base_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "First Name": ["Alice", "Bob", "Alice"],
            "AGE": [25.0, np.nan, 25.0],
            "City": ["  NY  ", " LA", "NY  "],
        }
    )


def test_rename_columns() -> None:
    """Columns with spaces become snake_case."""
    df, _ = clean_dataframe(_base_df())
    assert "first_name" in df.columns
    assert "age" in df.columns
    assert "city" in df.columns


def test_fill_missing_numeric() -> None:
    """NaN in a numeric column is filled with its median."""
    df, _ = clean_dataframe(_base_df())
    assert df["age"].isna().sum() == 0


def test_drop_duplicates() -> None:
    """Duplicate rows are removed."""
    df, _ = clean_dataframe(_base_df())
    assert len(df) == 2  # Alice row was duplicated


def test_cleaning_log_not_empty() -> None:
    """Log has at least one entry after cleaning."""
    _, log = clean_dataframe(_base_df())
    assert len(log) > 0


def test_cleaning_config_disable_steps() -> None:
    """Disabling rename_columns leaves original column names intact."""
    config = CleaningConfig(rename_columns=False)
    df, _ = clean_dataframe(_base_df(), config)
    assert "First Name" in df.columns
    assert "AGE" in df.columns
