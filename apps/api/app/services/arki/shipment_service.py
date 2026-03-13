"""
배송(선적) 관리 서비스 (업무 도메인)
"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.shipment import Shipment


async def list_shipments(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[Shipment], int]:
    """배송 목록 조회"""
    stmt = select(Shipment)

    if purchase_order_id := filters.get("purchase_order_id"):
        stmt = stmt.where(Shipment.purchase_order_id == purchase_order_id)
    if shipment_status := filters.get("shipment_status"):
        stmt = stmt.where(Shipment.shipment_status == shipment_status)
    if customs_status := filters.get("customs_status"):
        stmt = stmt.where(Shipment.customs_status == customs_status)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(Shipment.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_shipment(
    data: dict[str, Any],
    db: AsyncSession,
) -> Shipment:
    """배송 생성"""
    shipment = Shipment(**data)
    db.add(shipment)
    await db.flush()
    return shipment


async def update_shipment(
    shipment_id: uuid.UUID,
    data: dict[str, Any],
    db: AsyncSession,
) -> Shipment:
    """배송 수정"""
    stmt = select(Shipment).where(Shipment.id == shipment_id)
    result = await db.execute(stmt)
    shipment = result.scalar_one_or_none()
    if not shipment:
        raise NotFoundException("Shipment not found")

    for key, value in data.items():
        if hasattr(shipment, key):
            setattr(shipment, key, value)

    await db.flush()
    return shipment
