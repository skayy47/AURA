from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from api.deps import get_session
from utils.exporters import to_csv, to_excel, to_json, to_parquet

router = APIRouter()

MIME = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "json": "application/json",
    "parquet": "application/octet-stream",
}
EXPORTERS = {"csv": to_csv, "xlsx": to_excel, "json": to_json, "parquet": to_parquet}

@router.get("/export/{session_id}/{format}")
async def export(session_id: str, format: str):
    if format not in EXPORTERS:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
    try:
        sess = get_session(session_id)
        df = sess.get("cleaned_df") or sess.get("raw_df")
        data = EXPORTERS[format](df)
        return Response(
            content=data,
            media_type=MIME[format],
            headers={"Content-Disposition": f"attachment; filename=aura_export.{format}"},
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
