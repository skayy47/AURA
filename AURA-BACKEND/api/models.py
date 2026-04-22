from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Meta(BaseModel):
    file_name: str
    file_size_kb: float
    rows: int
    cols: int
    format: str
    missing_count: int
    columns: List[str]
    dtypes: Dict[str, str]

class IngestResponse(BaseModel):
    session_id: str
    meta: Meta
    preview: List[Dict[str, Any]]   # first 5 rows as records

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
    log: List[Dict[str, Any]]

class ExploreResponse(BaseModel):
    session_id: str
    profile: Dict[str, Any]         # per-column stats
    numeric_cols: List[str]
    categorical_cols: List[str]
    datetime_cols: List[str]
    missing_heatmap: List[Dict[str, Any]]

class AskRequest(BaseModel):
    session_id: str
    question: str
    provider: str = "claude"        # "claude" | "openai"

class ExportRequest(BaseModel):
    session_id: str
    format: str                     # "csv" | "xlsx" | "json" | "parquet"
