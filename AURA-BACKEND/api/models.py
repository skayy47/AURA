"""Pydantic request/response models for the AURA API."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

class Meta(BaseModel):
    file_name: str
    file_size_kb: float
    rows: int
    cols: int
    format: str
    missing_count: int
    columns: list[str]
    dtypes: dict[str, str]


class IngestResponse(BaseModel):
    session_id: str
    meta: Meta
    preview: list[dict[str, Any]]   # first 5 rows as records


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


class ExploreResponse(BaseModel):
    session_id: str
    profile: dict[str, Any]         # per-column stats
    numeric_cols: list[str]
    categorical_cols: list[str]
    datetime_cols: list[str]
    missing_heatmap: list[dict[str, Any]]


class AskRequest(BaseModel):
    session_id: str
    question: str
    provider: str = "claude"        # "claude" | "openai"


class ExportRequest(BaseModel):
    session_id: str
    format: str                     # "csv" | "xlsx" | "json" | "parquet"
