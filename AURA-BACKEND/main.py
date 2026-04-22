from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import ingest, clean, explore, ai, export

app = FastAPI(title="AURA API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://aura.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api")
app.include_router(clean.router, prefix="/api")
app.include_router(explore.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(export.router, prefix="/api")

@app.get("/health")
def health(): return {"status": "ok", "version": "3.0.0"}
