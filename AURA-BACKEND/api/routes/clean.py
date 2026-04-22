from fastapi import APIRouter, HTTPException
from api.deps import get_session, update_session
from api.models import CleaningConfigRequest, CleanResponse
from engines.cleaning import clean_dataframe, CleaningConfig

router = APIRouter()

@router.post("/clean", response_model=CleanResponse)
async def clean(req: CleaningConfigRequest):
    try:
        sess = get_session(req.session_id)
        df = sess["raw_df"]
        rows_before, cols_before = df.shape

        config = CleaningConfig(
            rename_columns=req.rename_columns,
            normalize_strings=req.normalize_strings,
            detect_dates=req.detect_dates,
            remove_empty_cols=req.remove_empty_cols,
            fill_missing=req.fill_missing,
            drop_duplicates=req.drop_duplicates,
        )

        cleaned, log = clean_dataframe(df, config)
        update_session(req.session_id, {"cleaned_df": cleaned, "cleaning_log": log})

        rows_after, cols_after = cleaned.shape
        return CleanResponse(
            session_id=req.session_id,
            rows_before=rows_before, rows_after=rows_after,
            cols_before=cols_before, cols_after=cols_after,
            log=log,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
