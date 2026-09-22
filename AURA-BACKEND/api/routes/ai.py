import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api.deps import get_session, update_session
from api.models import AskRequest
from utils.helpers import get_logger
from engines.ai_insights import (
    ask_ai,
    coerce_provider,
    available_providers,
    is_configured,
    _DEFAULT_ORDER,
    AIProvider,
)

router = APIRouter()
logger = get_logger(__name__)


# Markers used only when the exception carries no HTTP status code.
# 404 / "model not found" MUST be retriable: a model pin the provider has since
# retired would otherwise kill the WHOLE fallback chain on the first provider
# instead of falling through to the next configured one. That is exactly the
# failure this endpoint hit in production once both gemini-2.0-flash and
# llama-3.3-70b-versatile were deprecated by their providers.
_RETRIABLE_MARKERS = (
    "429",
    "resource_exhausted",
    "quota",
    "rate_limit",
    "401",
    "403",
    "404",
    "model_not_found",
    "not_found",
    "does not exist",
    "no longer available",
    "deprecated",
    "decommissioned",
    "500",
    "502",
    "503",
    "504",
    "overloaded",
    "timeout",
    "connection",
)


def _is_retriable(exc: Exception) -> bool:
    """True when the NEXT provider in the chain deserves a try.

    Any HTTP-level failure from a provider (4xx or 5xx) qualifies: a rejected
    key, an exhausted quota and a model that no longer exists all mean "this
    provider cannot serve us, ask the next one". Only local bugs (TypeError,
    KeyError, ...) carry neither a status code nor a marker, and those are
    surfaced instead of being masked by silently cycling through providers.
    """
    status = getattr(exc, "status_code", None)
    if status is None:
        status = getattr(getattr(exc, "response", None), "status_code", None)
    if isinstance(status, int):
        return status >= 400

    text = str(exc).lower()
    return any(m in text for m in _RETRIABLE_MARKERS)


def _clean_error(exc: Exception) -> str:
    s = str(exc)
    if (
        "429" in s
        or "RESOURCE_EXHAUSTED" in s
        or "quota" in s.lower()
        or "rate_limit" in s.lower()
    ):
        return "⚠️ AI quota exceeded — all providers are rate-limited. Try again in a moment."
    if "401" in s or "403" in s:
        return "⚠️ AI authentication failed. Check your API key."
    if "404" in s:
        return "⚠️ AI model not found. The provider may have updated their API."
    return "⚠️ AI is unavailable right now. Please try again."


@router.get("/ai/providers")
def list_providers():
    """Report which AI providers are configured (free Groq + paid Claude/OpenAI)."""
    return {"providers": available_providers()}


@router.post("/ask")
async def ask(req: AskRequest):
    try:
        sess = get_session(req.session_id)
        df = sess.get("cleaned_df")
        if df is None:
            df = sess.get("raw_df")
        if df is None:
            raise HTTPException(status_code=422, detail="No dataset in session")

        provider = coerce_provider(req.provider)
        semantics = sess.get("semantics")
        analysis = sess.get(f"analysis_{req.language}") or sess.get("analysis_en")

        history = sess.get("chat_history", [])
        history.append({"role": "user", "content": req.question})
        update_session(req.session_id, {"chat_history": history})

        # Fallback chain: requested provider first, then all configured ones (free-first order)
        providers_to_try: list[AIProvider] = [provider]
        for p in _DEFAULT_ORDER:
            if p != provider and is_configured(p):
                providers_to_try.append(p)

        def generate():
            full_response = ""
            for attempt in providers_to_try:
                full_response = ""
                emitted = False
                try:
                    for chunk in ask_ai(
                        df,
                        req.question,
                        attempt,
                        stream=True,
                        semantics=semantics,
                        language=req.language,
                        analysis=analysis,
                    ):
                        full_response += chunk
                        emitted = True
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    break  # success — stop trying
                except Exception as exc:
                    logger.warning(
                        "AI provider %s failed (%s): %s",
                        getattr(attempt, "value", attempt),
                        "mid-stream" if emitted else "before first token",
                        exc,
                    )
                    # Only fall through BEFORE any text reached the client —
                    # switching providers mid-answer would splice two answers.
                    if (
                        not emitted
                        and _is_retriable(exc)
                        and attempt != providers_to_try[-1]
                    ):
                        continue  # silently try the next provider
                    full_response = _clean_error(exc)
                    yield f"data: {json.dumps({'chunk': full_response})}\n\n"
                    break

            history.append({"role": "assistant", "content": full_response})
            update_session(req.session_id, {"chat_history": history})
            yield f"data: {json.dumps({'done': True})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
