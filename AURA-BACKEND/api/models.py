"""Pydantic request/response models for the AURA API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class FileMeta(BaseModel):
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
    encoding_detected: str | None = None
    has_header: bool = True


# Kept as alias for any downstream code still importing `Meta`
Meta = FileMeta


class IngestResponse(BaseModel):
    session_id: str
    meta: FileMeta
    warnings: list[str] = []
    preview: list[dict[str, Any]]  # first 5 rows as records


class CleaningConfigRequest(BaseModel):
    session_id: str
    rename_columns: bool = True
    normalize_strings: bool = True
    detect_dates: bool = True
    remove_empty_cols: bool = True
    fill_missing: bool = True
    drop_duplicates: bool = True


class CleanResponse(BaseModel):
    session_id: str
    rows_before: int
    rows_after: int
    cols_before: int
    cols_after: int
    log: list[dict[str, Any]]
    score: float | None = None


class ExploreResponse(BaseModel):
    session_id: str
    profile: dict[str, Any]  # per-column stats
    numeric_cols: list[str]
    categorical_cols: list[str]
    datetime_cols: list[str]
    missing_heatmap: list[dict[str, Any]]


class AskRequest(BaseModel):
    session_id: str
    question: str
    provider: str = "claude"  # "claude" | "openai"
    language: str = "en"  # UI locale ("en" | "fr") — drives the AI response language


class ExportRequest(BaseModel):
    session_id: str
    format: str  # "csv" | "xlsx" | "json" | "parquet"
