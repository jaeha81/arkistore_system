import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import SlotStatus


class CapacitySlot(Base):
    __tablename__ = "capacity_slots"
    __table_args__ = (
        UniqueConstraint("slot_date", "delivery_team", "time_slot", name="uq_capacity_slot"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slot_date: Mapped[date] = mapped_column(Date, nullable=False)
    delivery_team: Mapped[str] = mapped_column(String(100), nullable=False)
    time_slot: Mapped[str] = mapped_column(String(50), nullable=False)
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    used_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    remaining_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    slot_status: Mapped[SlotStatus] = mapped_column(
        Enum(SlotStatus), nullable=False, default=SlotStatus.open
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
