import os
import re
from typing import Dict, List

import requests

LAPTOP_SERVICE_URL = os.getenv("LAPTOP_SERVICE_URL", "http://laptop-service:8000")
MOBILE_SERVICE_URL = os.getenv("MOBILE_SERVICE_URL", "http://mobile-service:8000")
PC_SERVICE_URL = os.getenv("PC_SERVICE_URL", "http://pc-service:8000")
KB_SERVICE_URL = os.getenv("KB_SERVICE_URL", "http://kb-service:8000")

SEGMENT_HINTS = {
    "gaming": "pc gaming gpu cpu hieu nang cao",
    "office": "laptop van phong pin nhe on dinh",
    "design": "workstation gpu ram render do hoa",
    "general": "thiet bi can bang gia hieu nang",
}


KB_DOCUMENTS: List[Dict[str, str]] = [
    {
        "doc_id": "kb_001",
        "title": "Catalog overview",
        "content": (
            "He thong co 3 nhom danh muc chinh: laptop, mobile, pc. Moi nhom co endpoint products va products/search "
            "de tra cuu nhanh theo ten, hang va cau hinh."
        ),
        "tags": ["catalog", "laptop", "mobile", "pc"],
        "source": "fallback",
    },
    {
        "doc_id": "kb_002",
        "title": "Laptop cho sinh vien IT",
        "content": (
            "Laptop cho sinh vien IT nen uu tien CPU 4-8 core, RAM tu 16GB, SSD 512GB tro len, trong luong nhe va pin tot. "
            "Neu lap trinh va di hoc nhieu, chon 13-14 inch se tien loi hon."
        ),
        "tags": ["laptop", "student", "programming", "it"],
        "source": "fallback",
    },
    {
        "doc_id": "kb_003",
        "title": "PC gaming va workstation",
        "content": (
            "PC gaming can GPU rieng, nguon on dinh va tan nhiet tot. Workstation can uu tien CPU, RAM va do on dinh "
            "khi render, design, va xu ly du lieu."
        ),
        "tags": ["pc", "gaming", "workstation", "gpu", "cpu"],
        "source": "fallback",
    },
    {
        "doc_id": "kb_004",
        "title": "Shopping guidance",
        "content": (
            "Nguoi dung co the mo ta nhu cau theo ngan sach, thuong hieu, loai san pham. AI uu tien tra ve san pham co trong kho "
            "va phu hop bo loc gia."
        ),
        "tags": ["budget", "shopping", "recommendation"],
        "source": "fallback",
    },
    {
        "doc_id": "kb_005",
        "title": "Checkout and inventory note",
        "content": (
            "Khi checkout, he thong can tru ton kho theo tung category. PC su dung co che select_for_update de tranh race condition "
            "khi dat hang dong thoi."
        ),
        "tags": ["checkout", "inventory", "concurrency"],
        "source": "fallback",
    },
]


def _tokenize(text: str) -> set[str]:
    # Keep Unicode word chars so Vietnamese tokens are not stripped out.
    normalized = re.sub(r"[^\w\s]", " ", text.lower(), flags=re.UNICODE)
    return {token for token in normalized.split() if len(token) > 2}


def _remote_kb_documents() -> List[Dict]:
    try:
        response = requests.get(f"{KB_SERVICE_URL}/kb/documents", timeout=3)
        if response.ok:
            documents = response.json()
            if isinstance(documents, list) and documents:
                return documents
    except requests.RequestException:
        pass
    return KB_DOCUMENTS


def _rank_kb(query: str, top_k: int = 2) -> List[Dict[str, str]]:
    try:
        response = requests.get(f"{KB_SERVICE_URL}/kb/search", params={"query": query, "top_k": top_k}, timeout=3)
        if response.ok:
            data = response.json()
            documents = data.get("documents", [])
            if isinstance(documents, list) and documents:
                ranked_docs = []
                for doc in documents:
                    ranked_docs.append(
                        {
                            "doc_id": doc.get("doc_id", ""),
                            "title": doc.get("title", ""),
                            "text": doc.get("content", ""),
                            "tags": doc.get("tags", []),
                            "source": doc.get("source", "kb-service"),
                        }
                    )
                return ranked_docs
    except requests.RequestException:
        pass

    documents = _remote_kb_documents()
    query_tokens = _tokenize(query)
    if not query_tokens:
        return [
            {
                "doc_id": doc.get("doc_id", ""),
                "title": doc.get("title", ""),
                "text": doc.get("content", doc.get("text", "")),
                "tags": doc.get("tags", []),
                "source": doc.get("source", "fallback"),
            }
            for doc in documents[:top_k]
        ]

    scored: List[tuple[int, Dict[str, str]]] = []
    for doc in documents:
        text = doc.get("content", doc.get("text", ""))
        title = doc.get("title", "")
        doc_tokens = _tokenize(text + " " + title)
        score = len(query_tokens.intersection(doc_tokens))
        scored.append((score, doc))

    scored.sort(key=lambda item: item[0], reverse=True)
    ranked = [doc for score, doc in scored[:top_k] if score > 0]
    if ranked:
        return [
            {
                "doc_id": doc.get("doc_id", ""),
                "title": doc.get("title", ""),
                "text": doc.get("content", doc.get("text", "")),
                "tags": doc.get("tags", []),
                "source": doc.get("source", "kb-service"),
            }
            for doc in ranked
        ]
    return [
        {
            "doc_id": doc.get("doc_id", ""),
            "title": doc.get("title", ""),
            "text": doc.get("content", doc.get("text", "")),
            "tags": doc.get("tags", []),
            "source": doc.get("source", "fallback"),
        }
        for doc in documents[:top_k]
    ]


def _fetch_catalog_summary() -> str:
    services = [
        ("laptop", LAPTOP_SERVICE_URL),
        ("mobile", MOBILE_SERVICE_URL),
        ("pc", PC_SERVICE_URL),
    ]
    chunks: List[str] = []

    for name, base_url in services:
        try:
            resp = requests.get(f"{base_url}/products", timeout=5)
            if not resp.ok:
                chunks.append(f"{name}: unavailable")
                continue

            items = resp.json().get("items", [])
            count = len(items)
            if not items:
                chunks.append(f"{name}: 0 items")
                continue

            prices = [int(item.get("price", 0)) for item in items if item.get("price") is not None]
            min_price = min(prices) if prices else 0
            max_price = max(prices) if prices else 0
            chunks.append(f"{name}: {count} items, price {min_price}-{max_price} VND")
        except requests.RequestException:
            chunks.append(f"{name}: unavailable")

    return " | ".join(chunks)


def retrieve_context(user_input: str, segment: str = "general") -> Dict[str, object]:
    segment_hint = SEGMENT_HINTS.get(segment, SEGMENT_HINTS["general"])
    enriched_query = f"{user_input} {segment_hint}".strip()
    kb_docs = _rank_kb(enriched_query)
    kb_context = "\n".join(f"[{doc['title']}] {doc['text']}" for doc in kb_docs)
    live_catalog = _fetch_catalog_summary()

    context = (
        f"User query: {user_input}\n"
        f"User segment: {segment}\n"
        f"Knowledge snippets:\n{kb_context}\n"
        f"Live catalog summary: {live_catalog}"
    )

    return {
        "source": "hybrid-rag",
        "query": user_input,
        "segment": segment,
        "documents": kb_docs,
        "catalog_summary": live_catalog,
        "context": context,
    }


def get_kb_documents() -> List[Dict[str, str]]:
    docs = _remote_kb_documents()
    return [
        {
            "doc_id": doc.get("doc_id", ""),
            "title": doc.get("title", ""),
            "text": doc.get("content", doc.get("text", "")),
            "tags": doc.get("tags", []),
            "source": doc.get("source", "kb-service"),
        }
        for doc in docs
    ]


def build_rag_debug(user_input: str) -> Dict[str, object]:
    ranked = _rank_kb(user_input, top_k=3)
    return {
        "query": user_input,
        "kb_top": ranked,
        "live_catalog": _fetch_catalog_summary(),
        "final": retrieve_context(user_input),
    }
