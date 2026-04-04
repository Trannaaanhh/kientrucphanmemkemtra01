import os
import re
from typing import Dict, List

import requests

LAPTOP_SERVICE_URL = os.getenv("LAPTOP_SERVICE_URL", "http://laptop-service:8000")
MOBILE_SERVICE_URL = os.getenv("MOBILE_SERVICE_URL", "http://mobile-service:8000")
PC_SERVICE_URL = os.getenv("PC_SERVICE_URL", "http://pc-service:8000")


KB_DOCUMENTS: List[Dict[str, str]] = [
    {
        "title": "catalog-overview",
        "text": (
            "He thong co 3 nhom danh muc chinh: laptop, mobile, pc. "
            "Moi nhom co endpoint products va products/search de tra cuu nhanh theo ten, hang va cau hinh."
        ),
    },
    {
        "title": "pc-knowledge",
        "text": (
            "Danh muc PC ho tro cac thuoc tinh dac thu: form_factor (desktop, gaming_pc, mini_pc, all_in_one, workstation), "
            "cpu_cores, gpu_vram_gb, usb_ports, hdmi_ports. Stock bang 0 thi status la out_of_stock, con hang thi available."
        ),
    },
    {
        "title": "shopping-guidance",
        "text": (
            "Nguoi dung co the mo ta nhu cau theo ngan sach (vi du 20 trieu, 30 trieu), thuong hieu, loai san pham. "
            "AI uu tien tra ve san pham co trong kho va phu hop bo loc gia."
        ),
    },
    {
        "title": "staff-gateway-flow",
        "text": (
            "Staff quan ly san pham qua endpoint /staff/products va co the loc category=all|laptop|mobile|pc. "
            "Gateway va customer-service deu da duoc cap nhat de ho tro danh muc pc trong catalog/search."
        ),
    },
    {
        "title": "inventory-checkout-note",
        "text": (
            "Khi checkout, he thong can tru ton kho theo tung category. "
            "PC su dung co che select_for_update de tranh race condition khi dat hang dong thoi."
        ),
    },
]


def _tokenize(text: str) -> set[str]:
    # Keep Unicode word chars so Vietnamese tokens are not stripped out.
    normalized = re.sub(r"[^\w\s]", " ", text.lower(), flags=re.UNICODE)
    return {token for token in normalized.split() if len(token) > 2}


def _rank_kb(query: str, top_k: int = 2) -> List[Dict[str, str]]:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return KB_DOCUMENTS[:top_k]

    scored: List[tuple[int, Dict[str, str]]] = []
    for doc in KB_DOCUMENTS:
        doc_tokens = _tokenize(doc["text"] + " " + doc["title"])
        score = len(query_tokens.intersection(doc_tokens))
        scored.append((score, doc))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [doc for score, doc in scored[:top_k] if score > 0] or KB_DOCUMENTS[:top_k]


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


def retrieve_context(user_input: str) -> Dict[str, str]:
    kb_docs = _rank_kb(user_input)
    kb_context = "\n".join(f"[{doc['title']}] {doc['text']}" for doc in kb_docs)
    live_catalog = _fetch_catalog_summary()

    context = (
        f"User query: {user_input}\n"
        f"Knowledge snippets:\n{kb_context}\n"
        f"Live catalog summary: {live_catalog}"
    )

    return {
        "source": "hybrid-rag",
        "context": context,
    }


def get_kb_documents() -> List[Dict[str, str]]:
    return KB_DOCUMENTS


def build_rag_debug(user_input: str) -> Dict[str, object]:
    ranked = _rank_kb(user_input, top_k=3)
    return {
        "query": user_input,
        "kb_top": ranked,
        "live_catalog": _fetch_catalog_summary(),
        "final": retrieve_context(user_input),
    }
