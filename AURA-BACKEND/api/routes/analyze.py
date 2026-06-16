"""Analysis route — ranked insights, quality, suggested questions.

Caches per-language in the session so repeated visits are instant.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.deps import get_session, update_session
from engines.analysis import analyze as run_analysis
from engines.exploration import profile_dataframe
from engines.semantics import infer_semantics
from engines.ai_insights import suggested_questions

router = APIRouter()


@router.get("/analyze/{session_id}")
async def analyze(session_id: str, lang: str = "en"):
    try:
        sess = get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

    language = lang[:2].lower()
    cache_key = f"analysis_{language}"

    # Return cached result if available
    cached = sess.get(cache_key)
    if cached is not None:
        return cached

    df = sess.get("cleaned_df")
    if df is None:
        df = sess.get("raw_df")
    if df is None:
        raise HTTPException(status_code=422, detail="No dataset in session")

    # Use cached profile/semantics from explore if available
    profile = sess.get("explore_profile")
    if profile is None:
        profile = profile_dataframe(df)

    semantics = sess.get("semantics")
    if semantics is None:
        semantics = infer_semantics(df, profile)

    meta_name = sess.get("meta_name", "dataset")
    analysis = run_analysis(df, profile, meta_name=meta_name, semantics=semantics, language=language)

    questions = suggested_questions(analysis, semantics=semantics, language=language)

    result = {
        "insights": analysis["insights"],
        "quality": analysis["quality"],
        "trends": analysis["trends"],
        "segments": analysis["segments"],
        "correlations": analysis["correlations"],
        "suggested_questions": questions,
    }

    update_session(session_id, {cache_key: result})
    return result
