"""
감사 로그 서비스: 관리자 액션 기록
critical action 발생 시 다른 서비스에서 호출
"""
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_action import AdminAction


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
