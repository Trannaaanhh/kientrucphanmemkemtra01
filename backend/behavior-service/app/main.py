from datetime import datetime, timezone

from fastapi import FastAPI
from sqlalchemy import select

from app.database import Base, SessionLocal, engine, ensure_database_exists
from app.features import build_profile, predict_from_profile
from app.models import BehaviorEvent
from app.schemas import (
    BehaviorBatchIn,
    BehaviorEventIn,
    BehaviorEventResult,
    PredictRequest,
    PredictResponse,
    ProfileResponse,
)

app = FastAPI(title="behavior-service", version="1.0.0")


def _infer_category(product_id: str | None) -> str | None:
    if not product_id:
        return None
    pid = product_id.strip().lower()
    if pid.startswith("l"):
        return "laptop"
    if pid.startswith("m"):
        return "mobile"
    if pid.startswith("p"):
        return "pc"
    return None


def _to_utc(ts: datetime | None) -> datetime:
    if ts is None:
        return datetime.now(timezone.utc)
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def _insert_event(payload: BehaviorEventIn) -> BehaviorEventResult:
    with SessionLocal() as db:
        if payload.event_id:
            existing = db.scalar(
                select(BehaviorEvent).where(BehaviorEvent.event_id == payload.event_id)
            )
            if existing:
                return BehaviorEventResult(event_id=payload.event_id, status="skipped")

        category = payload.product_category or _infer_category(payload.product_id) or "unknown"
        event = BehaviorEvent(
            event_id=payload.event_id,
            user_id=str(payload.user_id),
            event_type=payload.event_type,
            product_id=payload.product_id,
            product_category=category,
            query_text=payload.query_text,
            extracted_budget_vnd=payload.extracted_budget_vnd,
            quantity=max(int(payload.quantity or 1), 1),
            event_timestamp=_to_utc(payload.event_timestamp),
            event_metadata=payload.metadata,
        )
        db.add(event)
        db.commit()
        return BehaviorEventResult(event_id=payload.event_id, status="inserted")


@app.on_event("startup")
def startup():
    ensure_database_exists()
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "service": "behavior-service"}


@app.post("/behavior/events", response_model=BehaviorEventResult)
def ingest_event(payload: BehaviorEventIn):
    return _insert_event(payload)


@app.post("/behavior/events/batch")
def ingest_batch(payload: BehaviorBatchIn):
    inserted = 0
    skipped = 0
    for event in payload.events:
        result = _insert_event(event)
        if result.status == "inserted":
            inserted += 1
        else:
            skipped += 1
    return {"inserted": inserted, "skipped": skipped, "total": len(payload.events)}


@app.get("/behavior/profile/{user_id}", response_model=ProfileResponse)
def profile(user_id: str):
    with SessionLocal() as db:
        events = db.scalars(
            select(BehaviorEvent)
            .where(BehaviorEvent.user_id == str(user_id))
            .order_by(BehaviorEvent.event_timestamp.desc())
            .limit(300)
        ).all()

    data = build_profile(events)
    return ProfileResponse(user_id=str(user_id), **data)


@app.post("/behavior/predict", response_model=PredictResponse)
def predict(payload: PredictRequest):
    with SessionLocal() as db:
        events = db.scalars(
            select(BehaviorEvent)
            .where(BehaviorEvent.user_id == str(payload.user_id))
            .order_by(BehaviorEvent.event_timestamp.desc())
            .limit(300)
        ).all()

    profile_data = build_profile(events)
    prediction = predict_from_profile(profile_data, payload.current_context)

    return PredictResponse(user_id=str(payload.user_id), **prediction)
