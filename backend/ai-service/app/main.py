from fastapi import FastAPI
import os

import jwt
from fastapi import Header, HTTPException
from pydantic import BaseModel

from app.memory_store import append_history, get_user_history, list_histories
from app.pipeline import run_pipeline
from app.rag import build_rag_debug, get_kb_documents

app = FastAPI(title="ai-service", version="1.0.0")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-gateway-secret")
JWT_ALGO = "HS256"


class ChatRequest(BaseModel):
    message: str
    user_id: str


def _require_staff(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    if payload.get("role") != "staff":
        raise HTTPException(status_code=403, detail="Staff role required")


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-service"}


@app.post("/chat")
def chat(req: ChatRequest):
    user_id = str(req.user_id)
    append_history(user_id, "user", req.message)

    result = run_pipeline(req.message, user_id)
    assistant_text = result.get("response") or result.get("message") or str(result)
    append_history(user_id, "assistant", assistant_text, {"action": result.get("action")})

    return result


@app.get("/history")
def history(authorization: str | None = Header(default=None)):
    _require_staff(authorization)
    return {"sessions": list_histories()}


@app.get("/history/{user_id}")
def history_by_user(user_id: str, authorization: str | None = Header(default=None)):
    _require_staff(authorization)
    return {"user_id": user_id, "history": get_user_history(user_id)}


@app.get("/kb")
def kb(authorization: str | None = Header(default=None)):
    _require_staff(authorization)
    return {"source": "hybrid-rag", "documents": get_kb_documents()}


@app.get("/kb/debug")
def kb_debug(query: str, authorization: str | None = Header(default=None)):
    _require_staff(authorization)
    return build_rag_debug(query)
