from datetime import datetime, timezone

from sqlalchemy import JSON, BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BehaviorEvent(Base):
    __tablename__ = "behavior_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    event_type: Mapped[str] = mapped_column(String(32), index=True)
    product_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    product_category: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    query_text: Mapped[str | None] = mapped_column(String(512), nullable=True)
    extracted_budget_vnd: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    event_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
