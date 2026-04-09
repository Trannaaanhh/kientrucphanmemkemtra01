import os
from typing import Any, Dict

import requests

BEHAVIOR_SERVICE_URL = os.getenv("BEHAVIOR_SERVICE_URL", "http://behavior-service:8000")


def send_behavior_event(
    *,
    user_id: str,
    event_type: str,
    product_id: str | None = None,
    product_category: str | None = None,
    query_text: str | None = None,
    extracted_budget_vnd: int | None = None,
    quantity: int = 1,
    metadata: Dict[str, Any] | None = None,
) -> None:
    if not user_id:
        return

    payload = {
        "user_id": str(user_id),
        "event_type": event_type,
        "product_id": product_id,
        "product_category": product_category,
        "query_text": query_text,
        "extracted_budget_vnd": extracted_budget_vnd,
        "quantity": quantity,
        "metadata": metadata or {},
    }
    try:
        requests.post(f"{BEHAVIOR_SERVICE_URL}/behavior/events", json=payload, timeout=2)
    except requests.RequestException:
        return


def predict_behavior(user_id: str, current_context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    fallback = {
        "user_id": str(user_id),
        "segment_scores": {
            "gaming": 0.25,
            "office": 0.25,
            "design": 0.25,
            "general": 0.25,
        },
        "predicted_segment": "general",
        "purchase_probability": 0.2,
        "recommended_price_range": {"min_vnd": 8_000_000, "max_vnd": 25_000_000},
        "next_best_action": "show_segment_personalized_recommendations",
        "churn_risk_level": "medium",
    }

    if not user_id:
        return fallback

    payload = {
        "user_id": str(user_id),
        "current_context": current_context or {},
    }
    try:
        response = requests.post(
            f"{BEHAVIOR_SERVICE_URL}/behavior/predict",
            json=payload,
            timeout=2,
        )
        if not response.ok:
            return fallback
        data = response.json()
        return data if isinstance(data, dict) else fallback
    except requests.RequestException:
        return fallback
