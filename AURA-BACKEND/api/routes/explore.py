from fastapi import APIRouter, HTTPException

from api.deps import get_session, update_session
from engines.exploration import profile_dataframe, recommend_charts

router = APIRouter()


@router.get("/explore/{session_id}")
async def explore(session_id: str):
    try:
        sess = get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

    df = sess.get("cleaned_df")
    if df is None:
        df = sess.get("raw_df")
    if df is None:
        raise HTTPException(status_code=422, detail="No dataset in session")

    profile = profile_dataframe(df)
    recommendations = recommend_charts(df, profile)
    update_session(session_id, {"explore_profile": profile})

    return {
        "session_id": session_id,
        "profile": profile,
        "recommendations": recommendations,
        # Backward-compat convenience fields (still used by some frontend code paths)
        "numeric_cols": profile["numeric_cols"],
        "categorical_cols": profile["categorical_cols"],
        "datetime_cols": profile["datetime_cols"],
        "missing_heatmap": profile["missing_by_col"],
    }
