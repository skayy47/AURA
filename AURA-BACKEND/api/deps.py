"""Session store — in-memory primary, disk-backed for crash/restart persistence.

Sessions survive container crashes and OOM restarts. They do NOT survive
Docker image rebuilds (e.g. HF Space redeploy) unless SESSION_STORE_PATH
points to persistent storage (set to /data/sessions on HF Spaces with
persistent storage enabled).
"""
from __future__ import annotations

import logging
import os
import pickle
import time
import uuid
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_TTL = 4 * 60 * 60  # 4 hours in seconds

# Disk store directory — override via env var for persistence across rebuilds
_STORE_DIR = Path(os.getenv("SESSION_STORE_PATH", "/tmp/aura_sessions"))
try:
    _STORE_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass  # read-only filesystem — disk persistence silently disabled

# In-memory primary: {sid: {"data": dict, "expires": float}}
_store: dict[str, dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Disk helpers
# ---------------------------------------------------------------------------


def _path(sid: str) -> Path:
    return _STORE_DIR / f"{sid}.pkl"


def _save(sid: str, entry: dict) -> None:
    try:
        with open(_path(sid), "wb") as fh:
            pickle.dump(entry, fh, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as exc:
        logger.debug("Session disk-save skipped for %s: %s", sid, exc)


def _load(sid: str) -> dict | None:
    p = _path(sid)
    if not p.exists():
        return None
    try:
        with open(p, "rb") as fh:
            return pickle.load(fh)
    except Exception as exc:
        logger.debug("Session disk-load failed for %s: %s", sid, exc)
        try:
            p.unlink()
        except Exception:
            pass
        return None


def _delete_disk(sid: str) -> None:
    try:
        _path(sid).unlink()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# TTL purge
# ---------------------------------------------------------------------------


def _purge() -> None:
    now = time.time()
    expired = [sid for sid, e in _store.items() if e["expires"] < now]
    for sid in expired:
        del _store[sid]
        _delete_disk(sid)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def new_session() -> str:
    _purge()
    sid = str(uuid.uuid4())
    entry: dict[str, Any] = {"data": {}, "expires": time.time() + _TTL}
    _store[sid] = entry
    _save(sid, entry)
    return sid


def get_session(sid: str) -> dict[str, Any]:
    _purge()
    entry = _store.get(sid)
    if entry and entry["expires"] > time.time():
        return entry["data"]
    # Cache miss — try disk (happens after crash/restart)
    entry = _load(sid)
    if entry and entry["expires"] > time.time():
        _store[sid] = entry  # warm in-memory cache
        return entry["data"]
    raise KeyError(sid)


def update_session(sid: str, updates: dict[str, Any]) -> None:
    if sid not in _store:
        # Might be on disk only (post-restart)
        entry = _load(sid)
        if not entry or entry["expires"] <= time.time():
            raise KeyError(sid)
        _store[sid] = entry
    _store[sid]["data"].update(updates)
    _save(sid, _store[sid])
