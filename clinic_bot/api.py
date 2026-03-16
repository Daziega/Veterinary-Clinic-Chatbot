from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .basic_chat import basic_chat


app = FastAPI(title="Veterinary Clinic Chatbot API", version="0.1.0")


class BasicChatRequest(BaseModel):
    message: str


class BasicChatResponse(BaseModel):
    reply: str


@app.post("/chat-basic", response_model=BasicChatResponse)
async def chat_basic_endpoint(body: BasicChatRequest) -> BasicChatResponse:
    reply = basic_chat(message=body.message)
    return BasicChatResponse(reply=reply)

