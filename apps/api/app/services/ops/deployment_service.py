"""
배포 기록 관리 서비스 (운영 도메인)
프로젝트별 배포 이력 추적
"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.deployment_record import DeploymentRecord
from app.services.audit_service import log_action


async def list_deployments(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[DeploymentRecord], int]:
    """배포 기록 목록 조회"""
    stmt = select(DeploymentRecord)

    if project_id := filters.get("project_id"):
        stmt = stmt.where(DeploymentRecord.project_id == project_id)
    if site_id := filters.get("site_id"):
        stmt = stmt.where(DeploymentRecord.site_id == site_id)
    if environment := filters.get("environment"):
        stmt = stmt.where(DeploymentRecord.environment == environment)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(DeploymentRecord.deployed_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_deployment(
    data: dict[str, Any],
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> DeploymentRecord:
    """배포 기록 생성 + 감사 로그"""
    record = DeploymentRecord(
        **data,
        deployed_by=actor_user_id,
    )
    db.add(record)
    await db.flush()

    await log_action(
        db,
        actor_user_id=actor_user_id,
        action_type="deployment.create",
        target_table="deployment_records",
        target_id=str(record.id),
        after_data={
            "project_id": str(data.get("project_id")),
            "environment": str(data.get("environment")),
            "version_tag": data.get("version_tag"),
        },
    )
    return record


async def get_deployment(
    record_id: uuid.UUID,
    db: AsyncSession,
) -> DeploymentRecord:
    """배포 기록 단건 조회"""
    stmt = select(DeploymentRecord).where(DeploymentRecord.id == record_id)
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
    if not record:
        raise NotFoundException("Deployment record not found")
    return record
