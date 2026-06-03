"""AURA FastAPI backend — entry point."""
from __future__ import annotations

import os

from dotenv import load_dotenv

# Load local .env if present (no-op in prod where env vars are set directly).
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import ingest, clean, explore, ai, export, samples, billing

app = FastAPI(title="AURA API", version="5.0.0")

# Env-driven CORS (comma-separated). Always allow local dev.
_DEFAULT_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"
_origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", _DEFAULT_ORIGINS).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api")
app.include_router(clean.router, prefix="/api")
app.include_router(explore.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(samples.router, prefix="/api")
app.include_router(billing.router, prefix="/api")

@app.get("/health")
def health(): return {"status": "ok", "version": "5.0.0"}
