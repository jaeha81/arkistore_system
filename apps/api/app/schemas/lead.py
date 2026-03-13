"""
리드(문의) 스키마
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import LeadStatus


class LeadCreate(BaseModel):
    customer_id: UUID
    lead_channel: str
    inquiry_title: str
    inquiry_content: str | None = None
    assigned_to: UUID | None = None
    lead_status: LeadStatus = LeadStatus.new


class LeadUpdate(BaseModel):
    assigned_to: UUID | None = None
    lead_status: LeadStatus | None = None


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    lead_channel: str
    inquiry_title: str
    inquiry_content: str | None = None
    assigned_to: UUID | None = None
    lead_status: LeadStatus
    created_at: datetime
    updated_at: datetime
