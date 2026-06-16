import json
from dataclasses import asdict

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from api.deps import new_session, update_session
from api.models import FileMeta, IngestResponse
from engines.ingestion import load_file_bytes

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    file: UploadFile = File(...),
    promote_types: bool = Form(default=True),
    max_preview_rows: int = Form(default=5),
):
    """Ingest a structured file.

    Supports: CSV, TSV, Excel (multi-sheet), JSON (all orients + NDJSON), Parquet.
    Returns: session_id, full metadata, warnings list, and a preview.
    """
    if file.size and file.size > 200 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds 200 MB limit.")

    try:
        contents = await file.read()
        result = load_file_bytes(
            contents,
            filename=file.filename or "unknown",
            promote_types=promote_types,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")

    sid = new_session()
    update_session(
        sid,
        {
            "raw_df": result.df,
            "meta": asdict(result.meta),
            "ingest_warnings": result.warnings,
            "file_name": result.meta.name,
            "meta_name": result.meta.name,
        },
    )

    # Use pandas JSON serializer: handles all dtypes (category, datetime, numpy, NA)
    # without crashing on mixed/messy column types.
    preview: list[dict] = json.loads(
        result.df.head(max_preview_rows).to_json(
            orient="records", date_format="iso", default_handler=str
        )
    )

    return IngestResponse(
        session_id=sid,
        meta=FileMeta(**asdict(result.meta)),
        warnings=result.warnings,
        preview=preview,
    )
