"""
해피콜 스키마
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class HappyCallCreate(BaseModel):
    delivery_id: UUID
    call_date: datetime
    address_confirmed: bool = False
    ladder_confirmed: bool = False
    contact_confirmed: bool = False
    special_notes: str | None = None
    call_result: str


class HappyCallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    delivery_id: UUID
    call_date: datetime
    address_confirmed: bool
    ladder_confirmed: bool
    contact_confirmed: bool
    special_notes: str | None = None
    call_result: str
    created_at: datetime
