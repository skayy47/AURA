"""Export routes — CSV/Excel/JSON/Parquet + PDF report."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from api.deps import get_session
from utils.exporters import to_csv, to_excel, to_json, to_parquet

logger = logging.getLogger(__name__)
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
        df = sess.get("cleaned_df")
        if df is None:
            df = sess.get("raw_df")
        data = EXPORTERS[format](df)
        return Response(
            content=data,
            media_type=MIME[format],
            headers={
                "Content-Disposition": f"attachment; filename=aura_export.{format}"
            },
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/analyze/{session_id}")
async def analyze_session(session_id: str):
    """Run (and cache) the expert auto-analysis for a session → ranked insights."""
    try:
        sess = get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

    if sess.get("analysis"):
        return sess["analysis"]

    df = sess.get("cleaned_df")
    if df is None:
        df = sess.get("raw_df")
    if df is None:
        raise HTTPException(
            status_code=422, detail="No dataset in session — run ingest first"
        )

    try:
        profile = sess.get("explore_profile")
        if not profile:
            from engines.exploration import profile_dataframe

            profile = profile_dataframe(df)
            sess["explore_profile"] = profile
        from engines.analysis import analyze

        name = (sess.get("meta") or {}).get("name") or "dataset"
        result = analyze(df, profile, meta_name=name)
        sess["analysis"] = result
        return result
    except Exception as exc:
        logger.exception("Analysis failed")
        raise HTTPException(status_code=500, detail=f"Analysis error: {exc}") from exc


class PDFRequest(BaseModel):
    session_id: str


@router.post("/export/pdf")
async def export_pdf(body: PDFRequest):
    """Render a branded PDF report for the given session and return it as a download."""
    try:
        sess = get_session(body.session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

    profile = sess.get("explore_profile")
    if not profile:
        # Build a minimal profile from the cleaned/raw df on-the-fly
        df = sess.get("cleaned_df")
        if df is None:
            df = sess.get("raw_df")
        if df is None:
            raise HTTPException(
                status_code=422, detail="No dataset in session — run ingest first"
            )
        try:
            from engines.exploration import profile_dataframe

            profile = profile_dataframe(df)
            logger.info(
                "Built on-the-fly profile for PDF export (session %s)", body.session_id
            )
        except Exception as exc:
            logger.exception("Profile failed during PDF export")
            raise HTTPException(
                status_code=500, detail=f"Profiling error: {exc}"
            ) from exc

    try:
        from services.pdf_renderer import build_report_context, render_pdf

        context = build_report_context(sess, profile)
        pdf_bytes = await render_pdf(context)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("PDF render failed")
        raise HTTPException(status_code=500, detail=f"Render error: {exc}") from exc

    dataset_name = (sess.get("meta") or {}).get("name") or "report"
    safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in dataset_name)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="aura_{safe_name}.pdf"'},
    )
