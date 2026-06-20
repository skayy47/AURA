"""Sample dataset catalogue — GET /api/samples, GET /api/samples/{slug}/download, POST /api/samples/{slug}/load."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.deps import new_session, update_session
from engines.ingestion import load_file_bytes

router = APIRouter(tags=["samples"])

SAMPLES_DIR = Path(__file__).parent.parent.parent / "static" / "samples"

CATALOGUE: list[dict] = [
    {
        "slug": "mena-saas-revenue",
        "title": "MENA SaaS Revenue",
        "description": "620 B2B SaaS orders across the Gulf, Levant & North Africa — two years of revenue with a clear growth trend, segment spread, and a handful of mega-deal outliers. A time-series that leads with a headline trend chart.",
        "rows": 620,
        "cols": 13,
        "tags": ["time-series", "revenue", "MENA", "trend"],
        "file": "mena-saas-revenue.csv",
    },
    {
        "slug": "mena-workforce",
        "title": "MENA Workforce",
        "description": "515 employees across departments and seniority levels — salary, performance, bonus, satisfaction and tenure. A cross-sectional people-analytics set with strong hidden correlations and clear pay gaps.",
        "rows": 515,
        "cols": 12,
        "tags": ["people", "correlation", "MENA", "segments"],
        "file": "mena-workforce.csv",
    },
    {
        "slug": "mena-retail-raw",
        "title": "MENA Retail · raw dump",
        "description": "A deliberately messy export: junk headers, four different date formats, Yes/No/1/0 flags, ~20% duplicate rows and gaps everywhere. The full stress test for AURA's cleaning engine — yet it still resolves into a real dashboard.",
        "rows": 500,
        "cols": 11,
        "tags": ["messy", "cleaning", "MENA", "duplicates"],
        "file": "mena-retail-raw.csv",
    },
]

_SLUG_MAP = {s["slug"]: s for s in CATALOGUE}


@router.get("/samples")
def list_samples() -> list[dict]:
    return CATALOGUE


@router.get("/samples/{slug}/download")
def download_sample(slug: str):
    meta = _SLUG_MAP.get(slug)
    if not meta:
        raise HTTPException(404, detail=f"Sample '{slug}' not found")
    path = SAMPLES_DIR / meta["file"]
    if not path.exists():
        raise HTTPException(500, detail="Sample file missing on server")
    return StreamingResponse(
        iter([path.read_bytes()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{meta["file"]}"'},
    )


@router.post("/samples/{slug}/load")
def load_sample(slug: str) -> dict:
    """Ingest a sample dataset into a new session and return the standard IngestResponse shape."""
    meta = _SLUG_MAP.get(slug)
    if not meta:
        raise HTTPException(404, detail=f"Sample '{slug}' not found")
    path = SAMPLES_DIR / meta["file"]
    if not path.exists():
        raise HTTPException(500, detail="Sample file missing on server")

    result = load_file_bytes(path.read_bytes(), meta["file"])
    session_id = new_session()
    update_session(
        session_id,
        {
            "raw_df": result.df,
            "meta": result.meta.__dict__,
            "ingest_warnings": result.warnings,
            "file_name": meta["file"],
        },
    )

    # astype(object) first: low-cardinality columns get promoted to pandas
    # `category` dtype on ingest, and fillna("")/where on a Categorical rejects
    # the empty string as a new category. Cast to object, blank the NAs, stringify.
    head = result.df.head(20).astype(object)
    preview = head.where(head.notna(), "").astype(str).to_dict(orient="records")
    return {
        "session_id": session_id,
        "meta": result.meta.__dict__,
        "warnings": result.warnings,
        "preview": preview,
    }
