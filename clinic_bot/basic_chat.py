"""Lightweight stateless chat fallback (no tools, no memory, no RAG).

Kept as a simple fallback endpoint for basic Q&A when the full agent
is not needed or when OPENAI_API_KEY is the only available resource.
The system prompt references the clinic scope but does not claim
access to booking tools (since this module does not wire any).
"""
from __future__ import annotations

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

_SYSTEM_PROMPT = (
    "You are a friendly assistant for the ENAE25 Veterinary Clinic. "
    "The clinic provides dog and cat sterilisation (neutering/spaying), "
    "vaccinations, and microchip identification.\n\n"
    "Hard rules:\n"
    "- Do NOT give emergency or general-illness advice. Direct the owner "
    "to a full-service veterinary clinic or emergency hospital.\n"
    "- Do NOT make specific medical promises or diagnoses.\n"
    "- This is a lightweight endpoint without booking tools or detailed "
    "documentation access. For full booking support, use the main /chat "
    "endpoint instead.\n\n"
    "What you CAN do:\n"
    "- Explain general preparation for surgery (fasting, carrier, documents).\n"
    "- Encourage the owner to use the main chat for booking.\n"
    "- Answer basic questions about the clinic's services."
)


def _build_basic_llm() -> ChatOpenAI:
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


def basic_chat(message: str) -> str:
    """Handle a single user message with no tools, memory, or RAG."""
    llm = _build_basic_llm()
    result = llm.invoke([
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=message),
    ])
    return result.content
