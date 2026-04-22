"""Data ingestion engine — loads structured files into a pandas DataFrame."""
from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from utils.helpers import get_logger

logger = get_logger(__name__)

# 200 MB guard
_MAX_BYTES = 200 * 1024 * 1024


def load_file(file: Any) -> tuple[pd.DataFrame, dict]:
    """
    Load a structured file (CSV/TSV/Excel/JSON/Parquet) into a DataFrame.

    Returns:
        (df, meta) where meta = {name, size_kb, n_rows, n_cols, format}

    Raises:
        ValueError: for unsupported formats, oversized files, or parse errors.
    """
    filename: str = file.name
    suffix = Path(filename.lower()).suffix

    # Size guard
    file_bytes = file.read()
    size_bytes = len(file_bytes)
    if size_bytes > _MAX_BYTES:
        raise ValueError(
            f"File is {size_bytes / 1024 / 1024:.1f} MB — limit is 200 MB."
        )
    size_kb = round(size_bytes / 1024, 2)

    import io

    raw_io = io.BytesIO(file_bytes)

    try:
        if suffix == ".csv":
            df, fmt = _load_csv(raw_io), "CSV"
        elif suffix == ".tsv":
            df, fmt = _load_tsv(raw_io), "TSV"
        elif suffix in {".xls", ".xlsx"}:
            df, fmt = _load_excel(raw_io), "Excel"
        elif suffix == ".json":
            df, fmt = pd.read_json(raw_io), "JSON"
        elif suffix == ".parquet":
            df, fmt = pd.read_parquet(raw_io), "Parquet"
        else:
            raise ValueError(
                f"Format `{suffix}` is not supported. "
                "Use CSV, TSV, Excel (.xls/.xlsx), JSON, or Parquet."
            )
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(
            f"Could not parse the file. Check its content. Details: {exc}"
        ) from exc

    meta = {
        "name": filename,
        "size_kb": size_kb,
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "format": fmt,
    }
    logger.info("Loaded %s — %d rows × %d cols", filename, df.shape[0], df.shape[1])
    return df, meta


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_csv(buf: io.BytesIO) -> pd.DataFrame:
    """Try UTF-8 first, fall back to latin-1."""
    buf.seek(0)
    try:
        return pd.read_csv(buf, encoding="utf-8")
    except UnicodeDecodeError:
        buf.seek(0)
        return pd.read_csv(buf, encoding="latin-1")


def _load_tsv(buf: io.BytesIO) -> pd.DataFrame:
    """Try UTF-8 first, fall back to latin-1."""
    buf.seek(0)
    try:
        return pd.read_csv(buf, sep="\t", encoding="utf-8")
    except UnicodeDecodeError:
        buf.seek(0)
        return pd.read_csv(buf, sep="\t", encoding="latin-1")


def _load_excel(buf: io.BytesIO) -> pd.DataFrame:
    """Load first sheet; warn if multiple sheets exist."""
    xl = pd.ExcelFile(buf)
    sheet_names = xl.sheet_names
    if len(sheet_names) > 1:
        st.warning(
            f"Excel file has {len(sheet_names)} sheets: "
            f"{', '.join(sheet_names)}. Loading the first sheet: **{sheet_names[0]}**."
        )
    return xl.parse(sheet_names[0])
