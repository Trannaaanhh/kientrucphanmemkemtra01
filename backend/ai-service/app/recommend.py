import os
import re
from typing import Dict, List

import requests

LAPTOP_SERVICE_URL = os.getenv("LAPTOP_SERVICE_URL", "http://laptop-service:8000")
MOBILE_SERVICE_URL = os.getenv("MOBILE_SERVICE_URL", "http://mobile-service:8000")
PC_SERVICE_URL = os.getenv("PC_SERVICE_URL", "http://pc-service:8000")


def _extract_budget_vnd(raw_text: str) -> int | None:
    text = raw_text.lower()

    match = re.search(r"(\d+(?:[\.,]\d+)?)\s*(tr|triệu|trieu|m)\b", text)
    if match:
        value = float(match.group(1).replace(",", "."))
        return int(value * 1_000_000)

    match = re.search(r"(\d+(?:[\.,]\d+)?)\s*(k|ngh[iì]n|ngàn|ngan)\b", text)
    if match:
        value = float(match.group(1).replace(",", "."))
        return int(value * 1_000)

    return None


def _select_sources(query: str) -> List[str]:
    q = query.lower()
    has_laptop = "laptop" in q or "lap top" in q
    has_mobile = "mobile" in q or "dien thoai" in q or "điện thoại" in q or "phone" in q
    has_pc = "pc" in q or "desktop" in q or "may tinh ban" in q or "máy tính bàn" in q or "workstation" in q

    if has_laptop and not has_mobile and not has_pc:
        return [LAPTOP_SERVICE_URL]
    if has_mobile and not has_laptop and not has_pc:
        return [MOBILE_SERVICE_URL]
    if has_pc and not has_laptop and not has_mobile:
        return [PC_SERVICE_URL]
    return [LAPTOP_SERVICE_URL, MOBILE_SERVICE_URL, PC_SERVICE_URL]


def _category_hint(query: str) -> str:
    q = query.lower()
    if "laptop" in q or "lap top" in q:
        return "laptop"
    if "mobile" in q or "dien thoai" in q or "điện thoại" in q or "phone" in q:
        return "mobile"
    if "pc" in q or "desktop" in q or "may tinh ban" in q or "máy tính bàn" in q or "workstation" in q:
        return "pc"
    return ""


def _extract_search_query(raw_text: str) -> str:
    text = raw_text.lower().strip()
    text = text.replace("laptop", " laptop ").replace("lap top", " laptop ")

    # Keep only the first intent segment before command chaining words.
    separators = [",", ";", " them ", " thêm ", " mua ", " thanh toan", " thanh toán"]
    cut_at = len(text)
    for sep in separators:
        idx = text.find(sep)
        if idx != -1:
            cut_at = min(cut_at, idx)

    cleaned = text[:cut_at].strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _search(base_url: str, query: str) -> List[Dict]:
    q = query.strip()
    if not q:
        return []

    try:
        res = requests.get(f"{base_url}/products/search", params={"q": q}, timeout=5)
        if not res.ok:
            return []
        direct_items = res.json().get("items", [])
        if direct_items:
            return direct_items

        # Fallback by keyword tokens to support natural phrases like
        # "laptop asus gaming 30 trieu" against simple icontains search.
        tokens = [token for token in re.split(r"\s+", q.lower()) if len(token) > 2]
        if not tokens:
            return []

        merged: Dict[str, Dict] = {}
        for token in tokens:
            token_res = requests.get(f"{base_url}/products/search", params={"q": token}, timeout=5)
            if not token_res.ok:
                continue
            for item in token_res.json().get("items", []):
                item_id = str(item.get("id", ""))
                if item_id and item_id not in merged:
                    merged[item_id] = item

        return list(merged.values())
    except requests.RequestException:
        return []


def recommend_products(intent: Dict) -> List[Dict]:
    raw_query = intent.get("raw", "")
    query = _extract_search_query(raw_query)
    budget_vnd = _extract_budget_vnd(raw_query)

    # Only recommend when we can derive a concrete search query.
    # This prevents random/all-catalog suggestions.
    if not query:
        return []

    sources = _select_sources(query)
    items: List[Dict] = []
    for source in sources:
        items.extend(_search(source, query))

    if not items and query != raw_query.strip():
        for source in sources:
            items.extend(_search(source, raw_query.strip()))

    if budget_vnd is not None:
        items = [item for item in items if int(item.get("price", 0)) <= budget_vnd]

        # If nothing matched after strict budget filter, broaden by category keyword.
        if not items:
            hint = _category_hint(query)
            fallback_query = hint if hint else query
            fallback_items: List[Dict] = []
            for source in sources:
                fallback_items.extend(_search(source, fallback_query))
            items = [item for item in fallback_items if int(item.get("price", 0)) <= budget_vnd]

    items.sort(key=lambda item: int(item.get("price", 0)))

    return items[:5]
