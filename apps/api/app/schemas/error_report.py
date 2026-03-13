"""
에러 리포트 수집 스키마
"""
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import Environment, SiteType


class ErrorReportCreate(BaseModel):
    project_code: str
    site_type: SiteType
    environment: Environment
    app_version: str
    screen_name: str | None = None
    error_code: str
    error_message: str
    user_context: dict[str, Any] | None = None


class ErrorReportCreateResponse(BaseModel):
    report_id: UUID
    trace_id: str | None = None
    grouped: bool = False
