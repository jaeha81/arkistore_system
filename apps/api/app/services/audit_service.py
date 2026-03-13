"""
감사 로그 서비스: 관리자 액션 기록
critical action 발생 시 다른 서비스에서 호출
"""
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AdminAction(Base):
    """관리자 액션 감사 로그 테이블 (inline 정의)"""
    __tablename__ = "admin_actions"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    action_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_table: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    before_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


async def log_action(
    db: AsyncSession,
    *,
    actor_user_id: uuid.UUID,
    action_type: str,
    target_table: str,
    target_id: str | None = None,
    before_data: dict[str, Any] | None = None,
    after_data: dict[str, Any] | None = None,
    notes: str | None = None,
) -> AdminAction:
    """감사 로그 기록"""
    action = AdminAction(
        actor_user_id=actor_user_id,
        action_type=action_type,
        target_table=target_table,
        target_id=target_id,
        before_data=before_data,
        after_data=after_data,
        notes=notes,
    )
    db.add(action)
    await db.flush()
    return action
