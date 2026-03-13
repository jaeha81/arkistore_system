"""
리드(문의) 관리 서비스 (업무 도메인)
"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.lead import Lead


async def list_leads(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[Lead], int]:
    """리드 목록 조회"""
    stmt = select(Lead)

    if status := filters.get("lead_status"):
        stmt = stmt.where(Lead.lead_status == status)
    if channel := filters.get("lead_channel"):
        stmt = stmt.where(Lead.lead_channel == channel)
    if assigned_to := filters.get("assigned_to"):
        stmt = stmt.where(Lead.assigned_to == assigned_to)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(Lead.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_lead(
    data: dict[str, Any],
    db: AsyncSession,
) -> Lead:
    """리드 생성"""
    lead = Lead(**data)
    db.add(lead)
    await db.flush()
    return lead


async def update_lead(
    lead_id: uuid.UUID,
    data: dict[str, Any],
    db: AsyncSession,
) -> Lead:
    """리드 수정"""
    stmt = select(Lead).where(Lead.id == lead_id)
    result = await db.execute(stmt)
    lead = result.scalar_one_or_none()
    if not lead:
        raise NotFoundException("Lead not found")

    for key, value in data.items():
        if hasattr(lead, key):
            setattr(lead, key, value)

    await db.flush()
    return lead
