from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


EventType = Literal[
    "view",
    "search",
    "add_cart",
    "remove_cart",
    "checkout_start",
    "purchase",
    "abandon_cart",
    "chat_query",
]

ProductCategory = Literal["laptop", "mobile", "pc", "unknown"]


class BehaviorEventIn(BaseModel):
    event_id: str | None = None
    user_id: str
    event_type: EventType
    product_id: str | None = None
    product_category: ProductCategory | None = None
    query_text: str | None = None
    extracted_budget_vnd: int | None = None
    quantity: int = 1
    event_timestamp: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BehaviorBatchIn(BaseModel):
    events: list[BehaviorEventIn]


class BehaviorEventResult(BaseModel):
    event_id: str | None
    status: Literal["inserted", "skipped"]


class ProfileResponse(BaseModel):
    user_id: str
    preferred_categories: list[str]
    avg_budget_vnd: int
    purchase_count: int
    add_to_cart_count: int
    session_days_30d: int
    days_since_last_event: int | None
    churn_risk: float
    recent_events: int


class PredictRequest(BaseModel):
    user_id: str
    current_context: dict[str, Any] = Field(default_factory=dict)


class PredictResponse(BaseModel):
    user_id: str
    segment_scores: dict[str, float]
    predicted_segment: str
    purchase_probability: float
    recommended_price_range: dict[str, int]
    next_best_action: str
    churn_risk_level: Literal["low", "medium", "high"]
