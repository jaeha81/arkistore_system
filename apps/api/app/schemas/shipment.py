"""
선적 스키마
"""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ShipmentCreate(BaseModel):
    purchase_order_id: UUID
    bl_number: str
    shipping_company: str | None = None
    departure_date: date | None = None
    estimated_arrival_date: date | None = None
    customs_status: str = "pending"
    shipment_status: str = "in_transit"


class ShipmentUpdate(BaseModel):
    customs_status: str | None = None
    shipment_status: str | None = None
    estimated_arrival_date: date | None = None


class ShipmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    purchase_order_id: UUID
    bl_number: str
    shipping_company: str | None = None
    departure_date: date | None = None
    estimated_arrival_date: date | None = None
    actual_arrival_date: date | None = None
    customs_status: str
    shipment_status: str
    created_at: datetime
    updated_at: datetime
