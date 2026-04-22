import uuid
from typing import Dict, Any
from datetime import datetime, timedelta

# In-memory session store — no Redis needed for portfolio
_sessions: Dict[str, Dict[str, Any]] = {}
_TTL_HOURS = 4

def new_session() -> str:
    sid = str(uuid.uuid4())
    _sessions[sid] = {"created_at": datetime.utcnow(), "raw_df": None, "cleaned_df": None,
                       "meta": {}, "cleaning_log": [], "chat_history": [], "ocr_text": ""}
    _cleanup()
    return sid

def get_session(sid: str) -> Dict[str, Any]:
    if sid not in _sessions:
        raise KeyError(f"Session {sid} not found or expired")
    return _sessions[sid]

def update_session(sid: str, data: Dict[str, Any]) -> None:
    _sessions[sid].update(data)

def _cleanup():
    cutoff = datetime.utcnow() - timedelta(hours=_TTL_HOURS)
    expired = [k for k, v in _sessions.items() if v["created_at"] < cutoff]
    for k in expired:
        del _sessions[k]
