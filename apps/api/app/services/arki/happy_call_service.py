"""
해피콜 관리 서비스 (업무 도메인)
"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.happy_call import HappyCall


async def list_happy_calls(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[HappyCall], int]:
    """해피콜 목록 조회"""
    stmt = select(HappyCall)

    if delivery_id := filters.get("delivery_id"):
        stmt = stmt.where(HappyCall.delivery_id == delivery_id)
    if call_result := filters.get("call_result"):
        stmt = stmt.where(HappyCall.call_result == call_result)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(HappyCall.call_date.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_happy_call(
    data: dict[str, Any],
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> HappyCall:
    """해피콜 생성"""
    happy_call = HappyCall(**data, created_by=actor_user_id)
    db.add(happy_call)
    await db.flush()
    return happy_call
