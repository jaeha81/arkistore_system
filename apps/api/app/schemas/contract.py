"""
계약 스키마
"""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import ContractStatus


class ContractCreate(BaseModel):
    customer_id: UUID
    consultation_id: UUID | None = None
    contract_date: date
    contract_amount: Decimal
    deposit_amount: Decimal | None = None
    contract_status: ContractStatus = ContractStatus.draft
    delivery_required: bool = False
    remarks: str | None = None


class ContractUpdate(BaseModel):
    contract_status: ContractStatus | None = None
    deposit_amount: Decimal | None = None
    remarks: str | None = None


class ContractRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    contract_number: str | None = None
    customer_id: UUID
    consultation_id: UUID | None = None
    contract_date: date
    contract_amount: Decimal
    deposit_amount: Decimal | None = None
    contract_status: ContractStatus
    delivery_required: bool
    remarks: str | None = None
    created_at: datetime
    updated_at: datetime


class ContractAttachmentRequest(BaseModel):
    attachment_id: UUID
    attachment_type: str
    notes: str | None = None
