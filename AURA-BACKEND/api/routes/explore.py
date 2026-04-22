from fastapi import APIRouter, HTTPException
from api.deps import get_session
from engines.exploration import get_profile   # existing engine

router = APIRouter()

@router.get("/explore/{session_id}")
async def explore(session_id: str):
    try:
        sess = get_session(session_id)
        df = sess.get("cleaned_df") or sess.get("raw_df")
        if df is None:
            raise HTTPException(status_code=422, detail="No dataset in session")

        profile = get_profile(df)   # returns dict of column stats

        numeric_cols = list(df.select_dtypes(include="number").columns)
        categorical_cols = list(df.select_dtypes(include=["object", "category"]).columns)
        datetime_cols = list(df.select_dtypes(include=["datetime"]).columns)

        missing_heatmap = [
            {"column": col, "missing": int(df[col].isnull().sum()),
             "pct": round(df[col].isnull().mean() * 100, 1)}
            for col in df.columns
        ]

        return {
            "session_id": session_id,
            "profile": profile,
            "numeric_cols": numeric_cols,
            "categorical_cols": categorical_cols,
            "datetime_cols": datetime_cols,
            "missing_heatmap": missing_heatmap,
            "shape": {"rows": len(df), "cols": len(df.columns)},
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
