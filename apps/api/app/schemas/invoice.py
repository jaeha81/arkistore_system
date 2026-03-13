"""
인보이스 스키마
"""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InvoiceCreate(BaseModel):
    purchase_order_id: UUID
    invoice_number: str
    invoice_date: date
    invoice_amount: Decimal
    currency: str
    file_attachment_id: UUID | None = None


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    purchase_order_id: UUID
    invoice_number: str
    invoice_date: date
    invoice_amount: Decimal
    currency: str
    file_attachment_id: UUID | None = None
    created_at: datetime
