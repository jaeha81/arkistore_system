"""
재고 스키마
"""
from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import InventoryStatus


class InventoryUpdate(BaseModel):
    current_stock: Decimal
    reserved_stock: Decimal
    safety_stock: Decimal
    reason: str


class InventoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    warehouse_name: str
    current_stock: Decimal
    reserved_stock: Decimal
    available_stock: Decimal
    safety_stock: Decimal
    expected_inbound_date: date | None = None
    inventory_status: InventoryStatus
