"""Data cleaning engine with configurable steps and change logging."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_string_dtype,
)

from utils.helpers import get_logger

logger = get_logger(__name__)


@dataclass
class CleaningConfig:
    """Toggle individual cleaning steps on or off."""

    rename_columns: bool = True
    normalize_strings: bool = True
    detect_dates: bool = True
    remove_empty_cols: bool = True
    fill_missing: bool = True
    drop_duplicates: bool = True


# ---------------------------------------------------------------------------
# Individual cleaning steps (each returns modified df + log entry)
# ---------------------------------------------------------------------------


def _rename_columns(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Rename columns to snake_case, stripping special characters."""
    original = list(df.columns)
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace(r"[^0-9a-zA-Z_]", "", regex=True)
    )
    changed = [o for o, n in zip(original, df.columns) if o != n]
    return df, {
        "step": "Rename columns",
        "affected_columns": changed,
        "detail": f"Renamed {len(changed)} column(s) to snake_case",
    }


def _normalize_strings(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Strip whitespace and collapse internal spaces in string columns."""
    df = df.copy()
    affected: list[str] = []
    for col in df.columns:
        if is_string_dtype(df[col]):
            before = df[col].copy()
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
            )
            if not before.equals(df[col]):
                affected.append(col)
    return df, {
        "step": "Normalize strings",
        "affected_columns": affected,
        "detail": f"Stripped/collapsed whitespace in {len(affected)} column(s)",
    }


def _detect_dates(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Convert columns that look like dates (>70 % parseable) to datetime."""
    df = df.copy()
    affected: list[str] = []
    for col in df.columns:
        if is_datetime64_any_dtype(df[col]):
            continue
        try:
            converted = pd.to_datetime(df[col], errors="coerce")
            if converted.notna().mean() > 0.7:
                df[col] = converted
                affected.append(col)
        except Exception:
            pass
    return df, {
        "step": "Detect dates",
        "affected_columns": affected,
        "detail": f"Converted {len(affected)} column(s) to datetime",
    }


def _remove_empty_cols(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Drop columns that are entirely NaN."""
    before_cols = set(df.columns)
    df = df.dropna(axis=1, how="all")
    dropped = list(before_cols - set(df.columns))
    return df, {
        "step": "Remove empty columns",
        "affected_columns": dropped,
        "detail": f"Dropped {len(dropped)} fully-empty column(s)",
    }


def _fill_missing(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Fill NaNs: median for numeric, mode for strings, ffill for dates."""
    df = df.copy()
    detail_parts: list[str] = []
    affected: list[str] = []
    for col in df.columns:
        series = df[col]
        n_missing = int(series.isna().sum())
        if n_missing == 0:
            continue
        if is_numeric_dtype(series) and series.notna().any():
            df[col] = series.fillna(series.median())
            detail_parts.append(f"{col}: {n_missing} → median")
            affected.append(col)
        elif is_string_dtype(series):
            mode = series.mode()
            fill_val = mode.iloc[0] if not mode.empty else "Unknown"
            df[col] = series.fillna(fill_val)
            detail_parts.append(f"{col}: {n_missing} → '{fill_val}'")
            affected.append(col)
        elif is_datetime64_any_dtype(series):
            df[col] = series.ffill()
            detail_parts.append(f"{col}: {n_missing} → ffill")
            affected.append(col)
    detail = "; ".join(detail_parts) if detail_parts else "No missing values found"
    return df, {
        "step": "Fill missing values",
        "affected_columns": affected,
        "detail": detail,
    }


def _drop_duplicates(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Remove exact duplicate rows."""
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    return df, {
        "step": "Drop duplicates",
        "affected_columns": [],
        "detail": f"Removed {removed} duplicate row(s)",
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def clean_dataframe(
    df: pd.DataFrame,
    config: CleaningConfig = CleaningConfig(),
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Apply configurable cleaning steps to *df*.

    Returns:
        (cleaned_df, log) where log is a list of step-level dicts.
    """
    log: list[dict] = []

    steps = [
        (config.rename_columns, _rename_columns),
        (config.normalize_strings, _normalize_strings),
        (config.detect_dates, _detect_dates),
        (config.remove_empty_cols, _remove_empty_cols),
        (config.fill_missing, _fill_missing),
        (config.drop_duplicates, _drop_duplicates),
    ]

    for enabled, fn in steps:
        if not enabled:
            continue
        df, entry = fn(df)
        log.append(entry)
        logger.info("[Cleaning] %s — %s", entry["step"], entry["detail"])

    return df, log
