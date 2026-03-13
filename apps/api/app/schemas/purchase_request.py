"""
구매 요청 스키마
"""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import PurchaseRequestStatus


class PurchaseRequestItemInput(BaseModel):
    product_id: UUID
    requested_qty: Decimal


class PurchaseRequestCreate(BaseModel):
    request_source: str
    required_date: date | None = None
    reason_text: str | None = None
    items: list[PurchaseRequestItemInput] = Field(..., min_length=1)


class PurchaseRequestUpdate(BaseModel):
    request_status: PurchaseRequestStatus


class PurchaseRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    request_number: str | None = None
    request_source: str
    request_status: PurchaseRequestStatus
    required_date: date | None = None
    reason_text: str | None = None
    created_at: datetime
