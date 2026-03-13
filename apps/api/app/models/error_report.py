import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import Environment, IssueStatus, SiteType


class ErrorReport(Base):
    __tablename__ = "error_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    site_type: Mapped[SiteType] = mapped_column(Enum(SiteType), nullable=False)
    environment: Mapped[Environment] = mapped_column(Enum(Environment), nullable=False)
    app_version: Mapped[str] = mapped_column(String(50), nullable=False)
    screen_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    error_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    error_message_masked: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_context: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    report_status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus), nullable=False, default=IssueStatus.new
    )
    issue_group_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issue_groups.id"), nullable=True
    )
    trace_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
