"""
상담 스키마
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ConsultationCreate(BaseModel):
    customer_id: UUID
    manager_user_id: UUID
    consultation_type: str
    summary: str
    needs_text: str | None = None
    next_action: str | None = None
    consultation_date: datetime


class ConsultationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    manager_user_id: UUID
    consultation_type: str
    summary: str
    needs_text: str | None = None
    next_action: str | None = None
    consultation_date: datetime
    created_at: datetime
