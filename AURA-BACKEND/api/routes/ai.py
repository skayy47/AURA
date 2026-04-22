import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api.deps import get_session, update_session
from api.models import AskRequest
from engines.ai_insights import ask_ai, AIProvider

router = APIRouter()

@router.post("/ask")
async def ask(req: AskRequest):
    try:
        sess = get_session(req.session_id)
        df = sess.get("cleaned_df") or sess.get("raw_df")
        if df is None:
            raise HTTPException(status_code=422, detail="No dataset in session")

        provider = AIProvider.CLAUDE if req.provider == "claude" else AIProvider.OPENAI

        # Add user message to history
        history = sess.get("chat_history", [])
        history.append({"role": "user", "content": req.question})
        update_session(req.session_id, {"chat_history": history})

        def generate():
            full_response = ""
            for chunk in ask_ai(df, req.question, provider, stream=True):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            # Save final response
            history.append({"role": "assistant", "content": full_response})
            update_session(req.session_id, {"chat_history": history})
            yield f"data: {json.dumps({'done': True})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
