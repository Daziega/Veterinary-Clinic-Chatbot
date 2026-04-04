from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mangum import Mangum
from pydantic import BaseModel, Field

from clinic_bot.agent import build_agent, invoke_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("vet_clinic")

_BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="ENAE25 Veterinary Clinic Chatbot", version="2.0.0")

_static_dir = _BASE_DIR / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")
else:
    logger.warning("Static directory not found at %s — static assets will 404", _static_dir)

_templates_dir = _BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))

handler = Mangum(app)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message text")
    session_id: str = Field(default="default", description="Session identifier for conversation memory")


class ChatResponse(BaseModel):
    reply: str


_agent = build_agent()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    global _agent

    logger.info("session=%s  user_msg=%s", body.session_id, body.message[:120])

    if _agent is None:
        _agent = build_agent()
        if _agent is None:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY is not set. Please configure it to use the chatbot.",
            )

    try:
        reply = invoke_agent(_agent, body.message, body.session_id)
        logger.info("session=%s  bot_reply=%s", body.session_id, reply[:120])
        return ChatResponse(reply=reply)
    except Exception as exc:
        logger.exception("session=%s  error=%s", body.session_id, exc)
        raise HTTPException(status_code=500, detail=f"Error: {exc}") from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
