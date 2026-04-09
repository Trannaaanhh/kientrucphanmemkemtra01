from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class KBDocumentIn(BaseModel):
    doc_id: str | None = None
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)
    source: str = "manual"
    embedding: list[float] = Field(default_factory=list)


class KBDocumentOut(BaseModel):
    doc_id: str
    title: str
    content: str
    tags: list[str]
    source: str
    embedding: list[float]
    created_at: datetime
    updated_at: datetime


class KBSearchResponse(BaseModel):
    query: str
    top_k: int
    documents: list[KBDocumentOut]
    summary: str


class KBUpsertResponse(BaseModel):
    doc_id: str
    status: str


class KBDebugResponse(BaseModel):
    query: str
    ranked_documents: list[dict[str, Any]]
    summary: str
