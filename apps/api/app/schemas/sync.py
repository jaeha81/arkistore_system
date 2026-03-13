"""
Google Sheets 동기화 스키마
"""
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import SyncJobStatus


class SheetExportRequest(BaseModel):
    project_code: str
    sheet_name: str
    dataset: list[dict[str, Any]]


class SheetSyncJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: UUID
    sheet_name: str
    job_type: str
    job_status: SyncJobStatus
