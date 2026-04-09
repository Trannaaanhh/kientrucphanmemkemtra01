from datetime import datetime, timedelta, timezone
from typing import Any

from app.models import BehaviorEvent

EVENT_WEIGHTS = {
    "view": 1,
    "search": 2,
    "add_cart": 3,
    "remove_cart": 1,
    "checkout_start": 4,
    "purchase": 5,
    "abandon_cart": 2,
    "chat_query": 1,
}


def _days_since(when: datetime | None) -> int | None:
    if not when:
        return None
    return max((datetime.now(timezone.utc) - when).days, 0)


def build_profile(events: list[BehaviorEvent]) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    if not events:
        return {
            "preferred_categories": ["unknown"],
            "avg_budget_vnd": 0,
            "purchase_count": 0,
            "add_to_cart_count": 0,
            "session_days_30d": 0,
            "days_since_last_event": None,
            "churn_risk": 0.75,
            "recent_events": 0,
        }

    category_scores = {"laptop": 0, "mobile": 0, "pc": 0}
    budgets: list[int] = []
    purchase_count = 0
    add_cart_count = 0

    event_timestamps: list[datetime] = []
    for event in events:
        event_timestamps.append(event.event_timestamp)
        if event.product_category in category_scores:
            category_scores[event.product_category] += EVENT_WEIGHTS.get(event.event_type, 1)

        if event.extracted_budget_vnd and event.extracted_budget_vnd > 0:
            budgets.append(int(event.extracted_budget_vnd))

        if event.event_type == "purchase":
            purchase_count += 1
        elif event.event_type == "add_cart":
            add_cart_count += max(int(event.quantity or 1), 1)

    sorted_categories = sorted(category_scores.items(), key=lambda item: item[1], reverse=True)
    preferred_categories = [name for name, score in sorted_categories if score > 0][:3] or ["unknown"]

    avg_budget = int(sum(budgets) / len(budgets)) if budgets else 0

    days_since_last_event = _days_since(max(event_timestamps) if event_timestamps else None)

    thirty_days_ago = now - timedelta(days=30)
    session_days = {
        event.event_timestamp.date().isoformat()
        for event in events
        if event.event_timestamp >= thirty_days_ago
    }

    churn_risk = 0.2
    if days_since_last_event is not None:
        churn_risk += min(days_since_last_event / 30.0, 0.6)
    if purchase_count == 0:
        churn_risk += 0.15

    return {
        "preferred_categories": preferred_categories,
        "avg_budget_vnd": avg_budget,
        "purchase_count": purchase_count,
        "add_to_cart_count": add_cart_count,
        "session_days_30d": len(session_days),
        "days_since_last_event": days_since_last_event,
        "churn_risk": round(min(churn_risk, 0.95), 3),
        "recent_events": len(events),
    }


def predict_from_profile(profile: dict[str, Any], current_context: dict[str, Any]) -> dict[str, Any]:
    scores = {
        "gaming": 0.25,
        "office": 0.25,
        "design": 0.25,
        "general": 0.25,
    }

    categories = profile.get("preferred_categories", [])
    avg_budget = int(profile.get("avg_budget_vnd") or 0)

    if "pc" in categories:
        scores["gaming"] += 0.25
    if "laptop" in categories:
        scores["office"] += 0.15
        scores["design"] += 0.1
    if "mobile" in categories:
        scores["general"] += 0.15

    if avg_budget >= 30_000_000:
        scores["gaming"] += 0.2
        scores["design"] += 0.15
    elif avg_budget >= 15_000_000:
        scores["office"] += 0.1
    elif 0 < avg_budget < 10_000_000:
        scores["general"] += 0.15

    category_hint = str(current_context.get("category_hint", "")).lower()
    if category_hint == "pc":
        scores["gaming"] += 0.1
    elif category_hint == "laptop":
        scores["office"] += 0.1
    elif category_hint == "mobile":
        scores["general"] += 0.1

    total = sum(scores.values()) or 1.0
    normalized = {name: round(value / total, 4) for name, value in scores.items()}

    predicted_segment = max(normalized.items(), key=lambda item: item[1])[0]

    purchase_probability = 0.15
    purchase_probability += min(profile.get("add_to_cart_count", 0) * 0.05, 0.25)
    purchase_probability += min(profile.get("purchase_count", 0) * 0.03, 0.2)
    if (profile.get("days_since_last_event") or 999) <= 2:
        purchase_probability += 0.1
    purchase_probability = round(min(purchase_probability, 0.95), 3)

    context_budget = int(current_context.get("extracted_budget", 0) or 0)
    budget_anchor = context_budget if context_budget > 0 else avg_budget
    if budget_anchor > 0:
        price_range = {
            "min_vnd": max(int(budget_anchor * 0.7), 1_000_000),
            "max_vnd": int(budget_anchor * 1.2),
        }
    else:
        price_range = {"min_vnd": 8_000_000, "max_vnd": 25_000_000}

    churn_risk = float(profile.get("churn_risk", 0.75))
    if churn_risk < 0.35:
        churn_risk_level = "low"
    elif churn_risk < 0.65:
        churn_risk_level = "medium"
    else:
        churn_risk_level = "high"

    if purchase_probability >= 0.55:
        action = "show_top_sellers"
    elif churn_risk_level == "high":
        action = "offer_support_or_discount"
    else:
        action = "show_segment_personalized_recommendations"

    return {
        "segment_scores": normalized,
        "predicted_segment": predicted_segment,
        "purchase_probability": purchase_probability,
        "recommended_price_range": price_range,
        "next_best_action": action,
        "churn_risk_level": churn_risk_level,
    }
