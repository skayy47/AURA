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
        "slug": "sales-mess",
        "title": "Sales Pipeline (messy)",
        "description": "40-row B2B sales log with duplicates, missing fields, and an outlier price. Good for practising the full clean → explore pipeline.",
        "rows": 40,
        "cols": 11,
        "tags": ["sales", "duplicates", "outliers", "nulls"],
        "file": "sales-mess.csv",
    },
    {
        "slug": "climate-sensors",
        "title": "MENA Climate Sensors",
        "description": "Multi-station time-series readings (Riyadh, Dubai, Cairo, Casablanca) with one sensor outlier and a missing temperature value.",
        "rows": 44,
        "cols": 12,
        "tags": ["time-series", "sensors", "outliers", "MENA"],
        "file": "climate-sensors.csv",
    },
    {
        "slug": "mena-orders",
        "title": "MENA E-Commerce Orders",
        "description": "50 regional orders across 11 countries with mixed payment methods, return flags, and delivery metrics — ideal for bar charts and category analysis.",
        "rows": 50,
        "cols": 13,
        "tags": ["e-commerce", "MENA", "categories", "clean"],
        "file": "mena-orders.csv",
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
    update_session(session_id, {
        "raw_df": result.df,
        "meta": result.meta.__dict__,
        "ingest_warnings": result.warnings,
        "file_name": meta["file"],
    })

    preview = result.df.head(20).fillna("").astype(str).to_dict(orient="records")
    return {
        "session_id": session_id,
        "meta": result.meta.__dict__,
        "warnings": result.warnings,
        "preview": preview,
    }
