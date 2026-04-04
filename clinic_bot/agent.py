"""Chat orchestration module.

Builds a tool-calling agent (LangGraph) with:
- System prompt loaded from prompt.md
- Session-based memory via MemorySaver (keyed by thread_id / session_id)
- Tools: availability checking, booking, date suggestions, and RAG retrieval
"""
from __future__ import annotations

import logging
import os

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from .prompt_loader import SYSTEM_PROMPT
from .rag import pre_surgery_tool
from .availability import (
    check_availability_tool,
    create_booking_tool,
    suggest_alternative_dates_tool,
)

logger = logging.getLogger(__name__)

ALL_TOOLS = [
    check_availability_tool,
    create_booking_tool,
    suggest_alternative_dates_tool,
    pre_surgery_tool,
]

_memory = MemorySaver()


def build_agent():
    """Build the clinic chatbot agent.

    Returns None if OPENAI_API_KEY is not set.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        return None

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    agent = create_agent(
        model=llm,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=_memory,
    )

    logger.info("Agent built with %d tools: %s", len(ALL_TOOLS), [t.name for t in ALL_TOOLS])
    return agent


def invoke_agent(agent, message: str, session_id: str) -> str:
    """Send a user message to the agent and return the text reply.

    The session_id is passed as the LangGraph thread_id so each
    session maintains its own conversation history.
    """
    config = {"configurable": {"thread_id": session_id}}

    response = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
    )

    messages = response.get("messages", [])
    if not messages:
        return "I'm sorry, I couldn't generate a response."

    last_msg = messages[-1]
    content = getattr(last_msg, "content", None) or str(last_msg)
    return content
