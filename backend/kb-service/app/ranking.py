import re
from typing import Iterable

from app.models import KBDocument


DEFAULT_KEYWORDS = {
    "laptop": {"laptop", "notebook", "ultrabook", "sinh vien", "văn phòng", "van phong", "programming", "coding"},
    "mobile": {"mobile", "điện thoại", "dien thoai", "phone", "smartphone", "camera", "pin"},
    "pc": {"pc", "desktop", "gaming", "workstation", "gpu", "cpu", "render", "mini pc"},
}


def tokenize(text: str) -> set[str]:
    normalized = re.sub(r"[^\w\s]", " ", text.lower(), flags=re.UNICODE)
    return {token for token in normalized.split() if len(token) > 2}


def document_text(doc: KBDocument) -> str:
    return " ".join([doc.title or "", doc.content or "", " ".join(doc.tags or [])])


def score_document(query: str, doc: KBDocument) -> int:
    query_tokens = tokenize(query)
    if not query_tokens:
        return 0
    doc_tokens = tokenize(document_text(doc))
    score = len(query_tokens.intersection(doc_tokens))
    lowered = query.lower()
    for category, keywords in DEFAULT_KEYWORDS.items():
        if category in lowered:
            score += len(query_tokens.intersection(keywords))
    return score


def rank_documents(query: str, docs: Iterable[KBDocument], top_k: int = 3) -> list[dict]:
    scored = []
    for doc in docs:
        scored.append((score_document(query, doc), doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    ranked = []
    for score, doc in scored[:top_k]:
        ranked.append(
            {
                "doc_id": doc.doc_id,
                "title": doc.title,
                "content": doc.content,
                "tags": doc.tags or [],
                "source": doc.source,
                "embedding": doc.embedding or [],
                "score": score,
            }
        )
    return ranked
