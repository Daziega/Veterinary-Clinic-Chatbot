"""RAG module: FAISS vector store over the clinic's pre-surgery documentation.

Provides a StructuredTool that the agent can call to retrieve relevant
clinical and scheduling information from data/pre_surgery.txt.
"""
from __future__ import annotations

import logging
from pathlib import Path
from functools import lru_cache

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "pre_surgery.txt"

_CHUNK_SIZE = 500
_CHUNK_OVERLAP = 50
_RETRIEVER_K = 4


class PreSurgeryInfoInput(BaseModel):
    query: str = Field(
        description=(
            "A natural-language question or search query about pre-surgery "
            "preparation, aftercare, medication, scheduling rules, drop-off "
            "times, fasting, transport requirements, or clinic policies."
        )
    )


@lru_cache(maxsize=1)
def _build_vectorstore() -> FAISS:
    """Build (and cache) a FAISS vector store from the pre-surgery docs."""
    text = _DATA_PATH.read_text(encoding="utf-8")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
        separators=["\n---\n", "\n\n", "\n", " "],
    )
    docs = splitter.create_documents([text])
    logger.info("RAG: split pre-surgery text into %d chunks", len(docs))

    embeddings = OpenAIEmbeddings()
    store = FAISS.from_documents(docs, embeddings)
    logger.info("RAG: FAISS vector store built successfully")
    return store


def get_retriever():
    """Return a LangChain retriever over the clinic documentation."""
    return _build_vectorstore().as_retriever(search_kwargs={"k": _RETRIEVER_K})


def _retrieve_docs(query: str) -> str:
    """Retrieve relevant pre-surgery documentation for a query."""
    retriever = get_retriever()
    docs = retriever.invoke(query)
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


pre_surgery_tool = StructuredTool.from_function(
    func=_retrieve_docs,
    name="get_clinic_pre_surgery_info",
    description=(
        "Search the clinic's pre-surgery documentation and scheduling rules. "
        "Use this tool whenever the client asks about: preparation before surgery, "
        "fasting instructions, what to bring on surgery day, aftercare, medication, "
        "warning signs, drop-off times, pick-up times, carrier/transport requirements, "
        "blood tests, vaccination requirements, or booking/scheduling rules. "
        "Input should be the user's question or a relevant search query."
    ),
    args_schema=PreSurgeryInfoInput,
)
