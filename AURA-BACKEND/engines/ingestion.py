"""Production-grade data ingestion engine.

Loads structured files (CSV/TSV/Excel/JSON/Parquet) into a pandas DataFrame,
then runs a single vectorized profiling pass to emit rich metadata.

Public entry points:
    load_file_bytes(contents, filename, promote_types=True) -> IngestResult
    load_file(file) -> (df, meta_dict)  # legacy wrapper for Streamlit

Design goals:
    - Zero Python-level row loops in the profiling pass
    - Encoding + separator auto-detection for CSV/TSV
    - Multi-sheet Excel with largest-sheet selection
    - JSON: records / split / index / table / values + NDJSON
    - Object column promotion to numeric/datetime/bool/category
    - Structured logging + warnings list for UI surfacing
"""
from __future__ import annotations

import csv
import io
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# 200 MB hard guard
_MAX_BYTES = 200 * 1024 * 1024

# Encoding fallback chain after chardet's guess
_ENCODING_FALLBACKS = ("utf-8", "utf-8-sig", "latin-1", "cp1252")


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

@dataclass
class FileMeta:
    name: str
    size_kb: float
    format: str
    n_rows: int
    n_cols: int
    columns: list[str]
    dtypes: dict[str, str]
    missing_total: int
    missing_by_col: dict[str, int]
    duplicate_rows: int
    estimated_date_cols: list[str]
    estimated_id_cols: list[str]
    estimated_numeric_cols: list[str]
    estimated_cat_cols: list[str]
    memory_mb: float
    encoding_detected: str | None
    has_header: bool


@dataclass
class IngestResult:
    df: pd.DataFrame
    meta: FileMeta
    warnings: list[str] = field(default_factory=list)

    def meta_dict(self) -> dict[str, Any]:
        return asdict(self.meta)


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def load_file_bytes(
    contents: bytes,
    filename: str,
    promote_types: bool = True,
) -> IngestResult:
    """Load a structured file from raw bytes.

    Raises:
        ValueError: for unsupported formats, oversized files, or parse errors.
    """
    if len(contents) > _MAX_BYTES:
        raise ValueError(f"File is {len(contents) / 1024 / 1024:.1f} MB — limit is 200 MB.")

    size_kb = round(len(contents) / 1024, 2)
    suffix = Path(filename.lower()).suffix
    warnings: list[str] = []
    encoding: str | None = None
    has_header = True

    try:
        if suffix == ".csv":
            df, encoding = _load_csv(contents, sep=None)
            fmt = "CSV"
        elif suffix == ".tsv":
            df, encoding = _load_csv(contents, sep="\t")
            fmt = "TSV"
        elif suffix in {".xls", ".xlsx"}:
            df, excel_warnings = _load_excel(io.BytesIO(contents))
            warnings.extend(excel_warnings)
            fmt = "Excel"
        elif suffix == ".json":
            df = _load_json(io.BytesIO(contents))
            fmt = "JSON"
        elif suffix == ".parquet":
            df = pd.read_parquet(io.BytesIO(contents))
            fmt = "Parquet"
        else:
            raise ValueError(
                f"Format `{suffix}` is not supported. "
                "Use CSV, TSV, Excel (.xls/.xlsx), JSON, or Parquet."
            )
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Could not parse the file. Details: {exc}") from exc

    if df.empty:
        raise ValueError("File loaded but contains no rows.")

    if promote_types:
        df, promo_warnings = _promote_types(df)
        warnings.extend(promo_warnings)

    meta = _profile(
        df,
        name=filename,
        size_kb=size_kb,
        fmt=fmt,
        encoding=encoding,
        has_header=has_header,
    )

    logger.info(
        "Ingest %s — %s — %d rows x %d cols — %.1f KB",
        filename, fmt, meta.n_rows, meta.n_cols, size_kb,
    )

    return IngestResult(df=df, meta=meta, warnings=warnings)


def load_file(file: Any) -> tuple[pd.DataFrame, dict]:
    """Legacy wrapper for Streamlit. Returns (df, lean_meta_dict).

    New code should call load_file_bytes() for the full IngestResult.
    """
    contents = file.read()
    filename = getattr(file, "name", "unknown")
    result = load_file_bytes(contents, filename=filename, promote_types=False)
    return result.df, {
        "name": result.meta.name,
        "size_kb": result.meta.size_kb,
        "n_rows": result.meta.n_rows,
        "n_cols": result.meta.n_cols,
        "format": result.meta.format,
    }


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _detect_encoding(raw: bytes) -> str:
    """Detect encoding from the first 50 KB using chardet."""
    try:
        import chardet
        sample = raw[:50_000]
        result = chardet.detect(sample)
        return result.get("encoding") or "utf-8"
    except Exception:
        return "utf-8"


def _sniff_separator(raw: bytes, encoding: str) -> str:
    """Guess CSV separator from the first 4 KB."""
    try:
        sample = raw[:4096].decode(encoding, errors="replace")
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except Exception:
        return ","


def _load_csv(contents: bytes, sep: str | None) -> tuple[pd.DataFrame, str]:
    """Try detected encoding first, fall back through common encodings."""
    detected = _detect_encoding(contents)
    encodings_to_try = [detected, *[e for e in _ENCODING_FALLBACKS if e != detected]]
    delimiter = sep if sep is not None else _sniff_separator(contents, detected)

    last_err: Exception | None = None
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(
                io.BytesIO(contents),
                encoding=enc,
                sep=delimiter,
                on_bad_lines="skip",
                low_memory=False,
            )
            return df, enc
        except (UnicodeDecodeError, UnicodeError) as e:
            last_err = e
            continue
        except Exception as e:
            last_err = e
            continue

    raise ValueError(f"Could not decode CSV with any encoding. Last error: {last_err}")


def _load_excel(buf: io.BytesIO) -> tuple[pd.DataFrame, list[str]]:
    """Load all sheets, select the largest non-empty one."""
    xl = pd.ExcelFile(buf)
    sheet_names = xl.sheet_names
    warnings: list[str] = []

    candidates: list[tuple[int, str, pd.DataFrame]] = []
    for name in sheet_names:
        try:
            df = xl.parse(name)
        except Exception as exc:
            warnings.append(f"Skipped sheet '{name}' — parse error: {exc}")
            continue
        if not df.empty:
            candidates.append((len(df), name, df))

    if not candidates:
        raise ValueError("All sheets in this Excel file are empty.")

    candidates.sort(key=lambda x: x[0], reverse=True)
    _, chosen_name, df = candidates[0]

    if len(sheet_names) > 1:
        warnings.append(
            f"Excel has {len(sheet_names)} sheets. Auto-selected '{chosen_name}' (largest)."
        )

    return df, warnings


def _load_json(buf: io.BytesIO) -> pd.DataFrame:
    """Parse JSON with orient auto-detection + NDJSON support + single-level flatten."""
    raw = buf.read().decode("utf-8", errors="replace").strip()
    if not raw:
        raise ValueError("JSON file is empty.")

    # NDJSON: one JSON object per line
    if "\n" in raw and raw.lstrip().startswith("{"):
        try:
            df = pd.read_json(io.StringIO(raw), lines=True)
            if not df.empty:
                return _flatten_dict_cols(df)
        except Exception:
            pass

    # Try standard orients
    for orient in ("records", "split", "index", "table", "values"):
        try:
            df = pd.read_json(io.StringIO(raw), orient=orient)
            if not df.empty:
                return _flatten_dict_cols(df)
        except Exception:
            continue

    # Last-ditch: parse as Python object then flatten
    try:
        obj = json.loads(raw)
        if isinstance(obj, list):
            return pd.json_normalize(obj)
        if isinstance(obj, dict):
            return pd.json_normalize([obj])
    except Exception:
        pass

    raise ValueError("Could not parse JSON. Expected an array of objects or a valid orient.")


def _flatten_dict_cols(df: pd.DataFrame) -> pd.DataFrame:
    """One-level flatten: expand object columns whose values are dicts."""
    for col in list(df.columns):
        mask = df[col].apply(lambda x: isinstance(x, dict))
        if mask.any():
            try:
                normalized = pd.json_normalize(df.loc[mask, col].tolist())
                normalized.columns = [f"{col}.{c}" for c in normalized.columns]
                normalized.index = df.index[mask]
                df = pd.concat([df.drop(columns=[col]), normalized], axis=1)
            except Exception:
                continue
    return df


# ---------------------------------------------------------------------------
# Type promotion
# ---------------------------------------------------------------------------

_BOOL_TRUTHY = {"true", "yes", "y", "1", "t"}
_BOOL_FALSY = {"false", "no", "n", "0", "f"}


def _promote_types(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Promote object columns to numeric / datetime / bool / category."""
    warnings: list[str] = []
    df = df.copy()

    for col in df.select_dtypes(include="object").columns:
        series = df[col].dropna()
        if series.empty:
            continue

        # Numeric
        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.notna().mean() > 0.9:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            continue

        # Datetime — tolerate warnings and test parseability
        try:
            dates = pd.to_datetime(series, errors="coerce", format="mixed")
        except Exception:
            dates = pd.to_datetime(series, errors="coerce")
        if dates.notna().mean() > 0.75:
            df[col] = pd.to_datetime(df[col], errors="coerce", format="mixed")
            continue

        # Boolean
        try:
            lower = series.astype(str).str.lower().str.strip()
            if lower.isin(_BOOL_TRUTHY | _BOOL_FALSY).mean() > 0.95:
                df[col] = lower.map(
                    {**{k: True for k in _BOOL_TRUTHY}, **{k: False for k in _BOOL_FALSY}}
                )
                continue
        except Exception:
            pass

        # Category — low cardinality relative to size
        try:
            n_unique = series.nunique()
            if n_unique > 0 and n_unique <= 50 and n_unique / max(len(series), 1) < 0.05:
                df[col] = df[col].astype("category")
        except Exception:
            continue

    return df, warnings


# ---------------------------------------------------------------------------
# Profiling (single vectorized pass)
# ---------------------------------------------------------------------------

def _profile(
    df: pd.DataFrame,
    *,
    name: str,
    size_kb: float,
    fmt: str,
    encoding: str | None,
    has_header: bool,
) -> FileMeta:
    n_rows = int(df.shape[0])
    n_cols = int(df.shape[1])
    columns = [str(c) for c in df.columns]
    dtypes = {str(c): str(t) for c, t in df.dtypes.items()}
    missing_by_col_series = df.isnull().sum()
    missing_by_col = {str(c): int(v) for c, v in missing_by_col_series.items()}
    missing_total = int(missing_by_col_series.sum())
    duplicate_rows = int(df.duplicated().sum())

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    datetime_cols = df.select_dtypes(include="datetime").columns.tolist()
    object_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    estimated_date_cols = [str(c) for c in datetime_cols]
    # Detect date-like object columns we didn't promote
    for col in object_cols:
        if col in estimated_date_cols:
            continue
        sample = df[col].dropna().astype(str).head(200)
        if sample.empty:
            continue
        try:
            parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
            if parsed.notna().mean() > 0.8:
                estimated_date_cols.append(str(col))
        except Exception:
            continue

    # ID-like columns = cardinality equals row count
    estimated_id_cols = [
        str(c) for c in df.columns
        if n_rows > 0 and df[c].nunique(dropna=False) == n_rows
    ]

    estimated_numeric_cols = [str(c) for c in numeric_cols]
    estimated_cat_cols = [
        str(c) for c in df.select_dtypes(include=["category"]).columns
    ] + [
        str(c) for c in object_cols
        if str(c) not in estimated_date_cols
        and str(c) not in estimated_id_cols
        and df[c].nunique(dropna=True) <= 50
    ]

    memory_mb = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 3)

    return FileMeta(
        name=name,
        size_kb=size_kb,
        format=fmt,
        n_rows=n_rows,
        n_cols=n_cols,
        columns=columns,
        dtypes=dtypes,
        missing_total=missing_total,
        missing_by_col=missing_by_col,
        duplicate_rows=duplicate_rows,
        estimated_date_cols=estimated_date_cols,
        estimated_id_cols=estimated_id_cols,
        estimated_numeric_cols=estimated_numeric_cols,
        estimated_cat_cols=estimated_cat_cols,
        memory_mb=memory_mb,
        encoding_detected=encoding,
        has_header=has_header,
    )
