import io
from fastapi import APIRouter, UploadFile, File, HTTPException
from api.deps import new_session, update_session
from api.models import IngestResponse, Meta
from engines.ingestion import load_file   # existing engine

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        buf = io.BytesIO(contents)
        buf.name = file.filename

        df, meta_raw = load_file(buf)   # existing engine returns (df, dict)

        sid = new_session()
        update_session(sid, {
            "raw_df": df,
            "meta": meta_raw,
            "file_name": file.filename,
        })

        meta = Meta(
            file_name=file.filename,
            file_size_kb=round(len(contents) / 1024, 1),
            rows=len(df),
            cols=len(df.columns),
            format=file.filename.split(".")[-1].upper(),
            missing_count=int(df.isnull().sum().sum()),
            columns=list(df.columns),
            dtypes={col: str(dtype) for col, dtype in df.dtypes.items()},
        )

        preview = df.head(5).fillna("—").astype(str).to_dict(orient="records")
        return IngestResponse(session_id=sid, meta=meta, preview=preview)

    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
