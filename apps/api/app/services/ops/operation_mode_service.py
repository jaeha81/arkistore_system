"""
운영 모드 전환 서비스 (운영 도메인)
프로젝트의 운영 모드를 제어하는 중요 액션
모드 변경은 항상 감사 로그와 함께 기록됨
"""
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import OperationMode
from app.core.exceptions import InvalidStatusTransitionException, ProjectNotFoundException
from app.models.project import Project
from app.services.audit_service import log_action

# 운영 모드 전이 허용 규칙
# G-08: 운영 도메인과 업무 도메인 분리 — 운영 모드는 ops 도메인 전용
ALLOWED_TRANSITIONS: dict[OperationMode, list[OperationMode]] = {
    OperationMode.normal: [OperationMode.maintenance, OperationMode.emergency],
    OperationMode.maintenance: [OperationMode.normal],
    OperationMode.emergency: [OperationMode.normal, OperationMode.maintenance],
}


async def get_current_mode(
    project_id: uuid.UUID,
    db: AsyncSession,
) -> dict[str, Any]:
    """프로젝트 현재 운영 모드 조회"""
    stmt = select(Project).where(Project.id == project_id, Project.deleted_at.is_(None))
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise ProjectNotFoundException()

    return {
        "project_id": str(project.id),
        "project_code": project.project_code,
        "operation_mode": project.operation_mode.value,
        "allowed_transitions": [m.value for m in ALLOWED_TRANSITIONS.get(project.operation_mode, [])],
    }


async def switch_mode(
    project_id: uuid.UUID,
    new_mode: OperationMode,
    reason: str,
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> dict[str, Any]:
    """
    운영 모드 전환
    - 전이 규칙 검증
    - 프로젝트 operation_mode 업데이트
    - 감사 로그 기록 (중요 액션)
    """
    stmt = select(Project).where(Project.id == project_id, Project.deleted_at.is_(None))
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise ProjectNotFoundException()

    current_mode = project.operation_mode
    if new_mode == current_mode:
        return {
            "project_id": str(project.id),
            "operation_mode": current_mode.value,
            "changed": False,
        }

    allowed = ALLOWED_TRANSITIONS.get(current_mode, [])
    if new_mode not in allowed:
        raise InvalidStatusTransitionException(
            f"Cannot switch from '{current_mode.value}' to '{new_mode.value}'"
        )

    project.operation_mode = new_mode
    await db.flush()

    await log_action(
        db,
        actor_user_id=actor_user_id,
        action_type="operation_mode.switch",
        target_table="projects",
        target_id=str(project_id),
        before_data={"operation_mode": current_mode.value},
        after_data={"operation_mode": new_mode.value, "reason": reason},
    )

    return {
        "project_id": str(project.id),
        "project_code": project.project_code,
        "operation_mode": new_mode.value,
        "changed": True,
    }
