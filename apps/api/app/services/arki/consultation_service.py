"""
상담 관리 서비스 (업무 도메인)
"""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.consultation import Consultation


async def list_consultations(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[Consultation], int]:
    """상담 목록 조회"""
    stmt = select(Consultation)

    if customer_id := filters.get("customer_id"):
        stmt = stmt.where(Consultation.customer_id == customer_id)
    if consultation_type := filters.get("consultation_type"):
        stmt = stmt.where(Consultation.consultation_type == consultation_type)
    if manager_user_id := filters.get("manager_user_id"):
        stmt = stmt.where(Consultation.manager_user_id == manager_user_id)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(Consultation.consultation_date.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_consultation(
    data: dict[str, Any],
    db: AsyncSession,
) -> Consultation:
    """상담 생성"""
    consultation = Consultation(**data)
    db.add(consultation)
    await db.flush()
    return consultation
