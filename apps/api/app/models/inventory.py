import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import InventoryStatus


class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), unique=True, nullable=False
    )
    warehouse_name: Mapped[str] = mapped_column(String(200), nullable=False)
    current_stock: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    reserved_stock: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    available_stock: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    safety_stock: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    expected_inbound_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    inventory_status: Mapped[InventoryStatus] = mapped_column(
        Enum(InventoryStatus), nullable=False, default=InventoryStatus.normal
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product")
