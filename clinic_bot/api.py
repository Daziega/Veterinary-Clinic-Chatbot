"""Secondary FastAPI sub-application with both basic and agent endpoints.

This module can be mounted alongside the main app or used independently.
The /chat-basic endpoint is a lightweight fallback; /chat-agent uses the
full LangGraph agent with tools, RAG, and memory.
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .basic_chat import basic_chat
from .agent import build_agent, invoke_agent

app = FastAPI(title="Veterinary Clinic Chatbot API", version="2.0.0")

_agent = build_agent()


class BasicChatRequest(BaseModel):
    message: str


class BasicChatResponse(BaseModel):
    reply: str


class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str = Field(default="default")


class AgentChatResponse(BaseModel):
    reply: str


@app.post("/chat-basic", response_model=BasicChatResponse)
async def chat_basic_endpoint(body: BasicChatRequest) -> BasicChatResponse:
    """Stateless endpoint -- no tools, no memory, no RAG."""
    reply = basic_chat(message=body.message)
    return BasicChatResponse(reply=reply)


@app.post("/chat-agent", response_model=AgentChatResponse)
async def chat_agent_endpoint(body: AgentChatRequest) -> AgentChatResponse:
    """Full agent endpoint with tools, RAG, and session memory."""
    global _agent
    if _agent is None:
        _agent = build_agent()
        if _agent is None:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set.")
    try:
        reply = invoke_agent(_agent, body.message, body.session_id)
        return AgentChatResponse(reply=reply)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
