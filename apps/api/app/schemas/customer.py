"""
고객 스키마
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import CustomerGrade


class CustomerCreate(BaseModel):
    customer_type: str = "individual"
    name: str
    phone: str | None = None
    email: str | None = None
    region: str | None = None
    source_channel: str | None = None
    grade: CustomerGrade = CustomerGrade.normal
    is_vip: bool = False


class CustomerUpdate(BaseModel):
    customer_type: str | None = None
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    region: str | None = None
    source_channel: str | None = None
    grade: CustomerGrade | None = None
    is_vip: bool | None = None


class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_type: str
    name: str
    phone_masked: str | None = None
    email_masked: str | None = None
    region: str | None = None
    source_channel: str | None = None
    grade: CustomerGrade
    is_vip: bool
    created_at: datetime
