"""
배송 캐파 슬롯 스키마
"""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import SlotStatus


class CapacitySlotCreate(BaseModel):
    slot_date: date
    delivery_team: str
    time_slot: str
    max_capacity: int


class CapacitySlotUpdate(BaseModel):
    max_capacity: int | None = None
    slot_status: SlotStatus | None = None


class CapacitySlotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slot_date: date
    delivery_team: str
    time_slot: str
    max_capacity: int
    used_capacity: int
    remaining_capacity: int
    slot_status: SlotStatus
    created_at: datetime
