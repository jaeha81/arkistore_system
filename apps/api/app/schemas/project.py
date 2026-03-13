"""
프로젝트 / 프로젝트 사이트 스키마
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import OperationMode, ProjectStatus, SiteType


# ── Project ──────────────────────────────────────────────

class ProjectCreate(BaseModel):
    project_code: str
    name: str
    client_name: str
    service_type: str
    main_url: str
    status: ProjectStatus = ProjectStatus.active
    operation_mode: OperationMode = OperationMode.normal


class ProjectUpdate(BaseModel):
    name: str | None = None
    client_name: str | None = None
    service_type: str | None = None
    main_url: str | None = None
    status: ProjectStatus | None = None
    operation_mode: OperationMode | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_code: str
    name: str
    client_name: str
    service_type: str
    main_url: str
    status: ProjectStatus
    operation_mode: OperationMode
    created_at: datetime
    updated_at: datetime


# ── ProjectSite ──────────────────────────────────────────

class ProjectSiteCreate(BaseModel):
    site_code: str
    site_name: str
    site_url: str
    site_type: SiteType
    is_enabled: bool = True


class ProjectSiteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    site_code: str
    site_name: str
    site_url: str
    site_type: SiteType
    is_enabled: bool
    created_at: datetime
