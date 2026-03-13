import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class HappyCall(Base):
    __tablename__ = "happy_calls"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deliveries.id"), nullable=False
    )
    call_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    address_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    ladder_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    contact_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    special_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    call_result: Mapped[str] = mapped_column(String(100), nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
