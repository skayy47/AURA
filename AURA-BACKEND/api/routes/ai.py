import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api.deps import get_session, update_session
from api.models import AskRequest
from engines.ai_insights import ask_ai, coerce_provider, available_providers

router = APIRouter()


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

        # Add user message to history
        history = sess.get("chat_history", [])
        history.append({"role": "user", "content": req.question})
        update_session(req.session_id, {"chat_history": history})

        def generate():
            full_response = ""
            try:
                for chunk in ask_ai(
                    df, req.question, provider, stream=True, semantics=semantics
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            except Exception as exc:
                msg = f"⚠️ AI is unavailable right now: {exc}"
                full_response = msg
                yield f"data: {json.dumps({'chunk': msg})}\n\n"
            # Save final response
            history.append({"role": "assistant", "content": full_response})
            update_session(req.session_id, {"chat_history": history})
            yield f"data: {json.dumps({'done': True})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
