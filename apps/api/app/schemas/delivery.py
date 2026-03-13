"""
배송 스키마
"""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import DeliveryStatus


class DeliveryCreate(BaseModel):
    contract_id: UUID
    customer_id: UUID
    delivery_date: date
    time_slot: str
    delivery_team: str
    vehicle_code: str | None = None
    address_text: str
    ladder_required: bool = False


class DeliveryUpdate(BaseModel):
    delivery_status: DeliveryStatus | None = None
    delivery_date: date | None = None
    time_slot: str | None = None


class DeliveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    delivery_number: str | None = None
    contract_id: UUID
    customer_id: UUID
    delivery_date: date
    time_slot: str
    delivery_team: str
    vehicle_code: str | None = None
    address_text: str
    ladder_required: bool
    delivery_status: DeliveryStatus
    created_at: datetime
