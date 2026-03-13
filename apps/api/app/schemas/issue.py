"""
이슈 / 에러 리포트 그룹 스키마
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import Environment, IssueStatus


class IssueSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_code: str
    environment: Environment
    app_version: str
    screen_name: str | None = None
    error_code: str
    error_message_masked: str | None = None
    report_status: IssueStatus
    occurred_at: datetime


class IssueStatusUpdate(BaseModel):
    status: IssueStatus
    reason: str | None = None


class IssueGroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    group_key: str
    group_title: str
    occurrence_count: int
    group_status: IssueStatus
    first_seen_at: datetime
    last_seen_at: datetime


class GithubIssueCreate(BaseModel):
    repository: str
    labels: list[str] = []


class GithubIssueCreateResponse(BaseModel):
    github_issue_number: int
    github_issue_url: str
    state: str
