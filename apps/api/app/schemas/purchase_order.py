"""
발주 스키마
"""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import PaymentStatus, PurchaseOrderStatus


class PurchaseOrderItemInput(BaseModel):
    product_id: UUID
    ordered_qty: Decimal
    unit_price: Decimal


class PurchaseOrderCreate(BaseModel):
    purchase_request_id: UUID | None = None
    supplier_name: str
    order_date: date
    currency: str
    items: list[PurchaseOrderItemInput] = Field(..., min_length=1)


class PurchaseOrderUpdate(BaseModel):
    payment_status: PaymentStatus | None = None
    order_status: PurchaseOrderStatus | None = None


class PurchaseOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_number: str | None = None
    purchase_request_id: UUID | None = None
    supplier_name: str
    order_date: date
    currency: str
    total_amount: Decimal
    payment_status: PaymentStatus
    order_status: PurchaseOrderStatus
    created_at: datetime
