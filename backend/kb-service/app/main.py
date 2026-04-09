from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import select

from app.database import Base, SessionLocal, engine, ensure_database_exists
from app.models import KBDocument
from app.ranking import rank_documents
from app.schemas import KBDebugResponse, KBDocumentIn, KBDocumentOut, KBSearchResponse, KBUpsertResponse
from app.seed import seed_documents

app = FastAPI(title="kb-service", version="1.0.0")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _to_output(doc: KBDocument) -> KBDocumentOut:
    return KBDocumentOut(
        doc_id=doc.doc_id,
        title=doc.title,
        content=doc.content,
        tags=doc.tags or [],
        source=doc.source,
        embedding=doc.embedding or [],
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


def _ranked_to_output(item: dict) -> KBDocumentOut:
    return KBDocumentOut(
        doc_id=item.get("doc_id", ""),
        title=item.get("title", ""),
        content=item.get("content", ""),
        tags=item.get("tags", []),
        source=item.get("source", "kb-service"),
        embedding=item.get("embedding", []),
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )


def _ensure_seeded() -> None:
    with SessionLocal() as session:
        seed_documents(session)


@app.on_event("startup")
def startup():
    ensure_database_exists()
    Base.metadata.create_all(bind=engine)
    _ensure_seeded()


@app.get("/health")
def health():
    return {"status": "ok", "service": "kb-service"}


@app.get("/kb/documents", response_model=list[KBDocumentOut])
def list_documents():
    with SessionLocal() as session:
        docs = session.scalars(select(KBDocument).order_by(KBDocument.updated_at.desc())).all()
    return [_to_output(doc) for doc in docs]


@app.get("/kb/documents/{doc_id}", response_model=KBDocumentOut)
def get_document(doc_id: str):
    with SessionLocal() as session:
        doc = session.scalar(select(KBDocument).where(KBDocument.doc_id == doc_id))
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return _to_output(doc)


@app.post("/kb/documents", response_model=KBUpsertResponse)
def create_document(payload: KBDocumentIn):
    doc_id = payload.doc_id or f"kb_{uuid4().hex[:8]}"
    with SessionLocal() as session:
        exists = session.scalar(select(KBDocument).where(KBDocument.doc_id == doc_id))
        if exists:
            raise HTTPException(status_code=409, detail="Document already exists")
        session.add(
            KBDocument(
                doc_id=doc_id,
                title=payload.title,
                content=payload.content,
                tags=payload.tags,
                embedding=payload.embedding,
                source=payload.source,
                updated_at=_utcnow(),
            )
        )
        session.commit()
    return KBUpsertResponse(doc_id=doc_id, status="created")


@app.put("/kb/documents/{doc_id}", response_model=KBUpsertResponse)
def update_document(doc_id: str, payload: KBDocumentIn):
    with SessionLocal() as session:
        doc = session.scalar(select(KBDocument).where(KBDocument.doc_id == doc_id))
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        doc.title = payload.title
        doc.content = payload.content
        doc.tags = payload.tags
        doc.embedding = payload.embedding
        doc.source = payload.source
        doc.updated_at = _utcnow()
        session.commit()
    return KBUpsertResponse(doc_id=doc_id, status="updated")


@app.delete("/kb/documents/{doc_id}", response_model=KBUpsertResponse)
def delete_document(doc_id: str):
    with SessionLocal() as session:
        doc = session.scalar(select(KBDocument).where(KBDocument.doc_id == doc_id))
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        session.delete(doc)
        session.commit()
    return KBUpsertResponse(doc_id=doc_id, status="deleted")


@app.get("/kb/search", response_model=KBSearchResponse)
def search_documents(query: str, top_k: int = Query(default=3, ge=1, le=10)):
    with SessionLocal() as session:
        docs = session.scalars(select(KBDocument)).all()
    ranked = rank_documents(query, docs, top_k=top_k)
    summary = " | ".join(f"{item['title']}: {item['score']}" for item in ranked) or "no results"
    return KBSearchResponse(query=query, top_k=top_k, documents=[_ranked_to_output(item) for item in ranked], summary=summary)


@app.get("/kb/debug", response_model=KBDebugResponse)
def debug(query: str, top_k: int = Query(default=3, ge=1, le=10)):
    with SessionLocal() as session:
        docs = session.scalars(select(KBDocument)).all()
    ranked = rank_documents(query, docs, top_k=top_k)
    summary = " | ".join(f"{item['title']}: {item['score']}" for item in ranked) or "no results"
    return KBDebugResponse(query=query, ranked_documents=ranked, summary=summary)
