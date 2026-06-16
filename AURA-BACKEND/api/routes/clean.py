from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException

from api.deps import get_session, update_session
from api.models import CleaningConfigRequest, CleanResponse
from engines.cleaning import CleaningConfig, CleaningOrchestrator

router = APIRouter()


@router.post("/clean", response_model=CleanResponse)
async def clean(req: CleaningConfigRequest):
    try:
        sess = get_session(req.session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

    raw_df = sess.get("raw_df")
    if raw_df is None:
        raise HTTPException(
            status_code=400,
            detail="No dataset loaded. Call /api/ingest first.",
        )

    rows_before, cols_before = raw_df.shape

    config = CleaningConfig(
        rename_columns=req.rename_columns,
        normalize_strings=req.normalize_strings,
        detect_dates=req.detect_dates,
        remove_empty_cols=req.remove_empty_cols,
        fill_missing=req.fill_missing,
        drop_duplicates=req.drop_duplicates,
    )

    orchestrator = CleaningOrchestrator()
    cleaned_df, report = orchestrator.clean(raw_df.copy(), config)

    update_session(
        req.session_id,
        {
            "cleaned_df": cleaned_df,
            "cleaning_log": report.steps,
        },
    )

    rows_after, cols_after = cleaned_df.shape

    # Extract quality score from the Schema Validator log entry.
    quality_score: float = 0.0
    for step in report.steps:
        m = re.search(r"Quality score:\s*([\d.]+)/100", step.get("detail", ""))
        if m:
            quality_score = float(m.group(1))
            break
    else:
        # Fallback: SchemaValidator was skipped or failed — compute from cleaned df
        try:
            n = cleaned_df.shape[0] * cleaned_df.shape[1]
            missing_rate = float(cleaned_df.isnull().sum().sum() / n) if n > 0 else 0.0
            quality_score = round(max(0.0, min(100.0, (1.0 - missing_rate * 2) * 100)), 1)
        except Exception:
            quality_score = 0.0

    update_session(
        req.session_id,
        {
            "cleaned_df": cleaned_df,
            "cleaning_log": report.steps,
            "quality_score": quality_score,
        },
    )

    return CleanResponse(
        session_id=req.session_id,
        rows_before=rows_before,
        rows_after=rows_after,
        cols_before=cols_before,
        cols_after=cols_after,
        log=report.steps,
        score=quality_score,
    )
