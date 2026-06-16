import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api.deps import get_session, update_session
from api.models import AskRequest
from engines.ai_insights import (
    ask_ai,
    coerce_provider,
    available_providers,
    is_configured,
    _DEFAULT_ORDER,
    AIProvider,
)

router = APIRouter()


def _is_retriable(exc: Exception) -> bool:
    s = str(exc)
    return any(x in s for x in ["429", "RESOURCE_EXHAUSTED", "quota", "rate_limit", "401", "403"])


def _clean_error(exc: Exception) -> str:
    s = str(exc)
    if "429" in s or "RESOURCE_EXHAUSTED" in s or "quota" in s.lower() or "rate_limit" in s.lower():
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
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    break  # success — stop trying
                except Exception as exc:
                    if _is_retriable(exc) and attempt != providers_to_try[-1]:
                        continue  # silently try next provider
                    full_response = _clean_error(exc)
                    yield f"data: {json.dumps({'chunk': full_response})}\n\n"
                    break

            history.append({"role": "assistant", "content": full_response})
            update_session(req.session_id, {"chat_history": history})
            yield f"data: {json.dumps({'done': True})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
