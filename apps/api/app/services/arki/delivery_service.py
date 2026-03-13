"""
배달(납품) 관리 서비스 (업무 도메인)
"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import DeliveryStatus
from app.core.exceptions import (
    DeliveryNotFoundException,
    IdempotencyConflictException,
    InvalidStatusTransitionException,
)
from app.models.delivery import Delivery
from app.services.arki.capacity_service import reserve_slot
from app.services.audit_service import log_action

# 배달 상태 전이 규칙
STATUS_TRANSITIONS: dict[DeliveryStatus, list[DeliveryStatus]] = {
    DeliveryStatus.scheduled: [
        DeliveryStatus.confirmed,
        DeliveryStatus.cancelled,
    ],
    DeliveryStatus.confirmed: [
        DeliveryStatus.in_transit,
        DeliveryStatus.delayed,
        DeliveryStatus.cancelled,
    ],
    DeliveryStatus.in_transit: [
        DeliveryStatus.completed,
        DeliveryStatus.delayed,
    ],
    DeliveryStatus.delayed: [
        DeliveryStatus.in_transit,
        DeliveryStatus.cancelled,
    ],
    DeliveryStatus.completed: [],
    DeliveryStatus.cancelled: [],
}


async def list_deliveries(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[Delivery], int]:
    """배달 목록 조회"""
    stmt = select(Delivery)

    if delivery_date := filters.get("delivery_date"):
        stmt = stmt.where(Delivery.delivery_date == delivery_date)
    if delivery_team := filters.get("delivery_team"):
        stmt = stmt.where(Delivery.delivery_team == delivery_team)
    if status := filters.get("delivery_status"):
        stmt = stmt.where(Delivery.delivery_status == status)
    if contract_id := filters.get("contract_id"):
        stmt = stmt.where(Delivery.contract_id == contract_id)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(Delivery.delivery_date.desc(), Delivery.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_delivery(
    data: dict[str, Any],
    idempotency_key: str | None,
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> Delivery:
    """
    배달 생성
    - 멱등성 체크
    - CAPA 슬롯 가용 확인 + 예약
    - 감사 로그
    """
    if idempotency_key:
        existing = await db.execute(
            select(Delivery)
            .where(Delivery.idempotency_key == idempotency_key)
            .limit(1)
        )
        if existing.scalar_one_or_none():
            raise IdempotencyConflictException("Duplicate delivery creation request")

    # CAPA 슬롯 예약
    await reserve_slot(
        slot_date=data["delivery_date"],
        delivery_team=data["delivery_team"],
        time_slot=data["time_slot"],
        db=db,
    )

    delivery = Delivery(
        **data,
        idempotency_key=idempotency_key,
    )
    db.add(delivery)
    await db.flush()

    await log_action(
        db,
        actor_user_id=actor_user_id,
        action_type="delivery.create",
        target_table="deliveries",
        target_id=str(delivery.id),
        after_data={
            "delivery_date": str(data["delivery_date"]),
            "delivery_team": data["delivery_team"],
            "time_slot": data["time_slot"],
        },
    )
    return delivery


async def update_delivery(
    delivery_id: uuid.UUID,
    data: dict[str, Any],
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> Delivery:
    """배달 수정 (상태 전이 검증 + 감사 로그)"""
    stmt = select(Delivery).where(Delivery.id == delivery_id)
    result = await db.execute(stmt)
    delivery = result.scalar_one_or_none()
    if not delivery:
        raise DeliveryNotFoundException()

    new_status = data.get("delivery_status")
    if new_status and new_status != delivery.delivery_status:
        allowed = STATUS_TRANSITIONS.get(delivery.delivery_status, [])
        if new_status not in allowed:
            raise InvalidStatusTransitionException(
                f"Cannot transition from {delivery.delivery_status.value} to {new_status.value}"
            )

    before_status = delivery.delivery_status.value

    for key, value in data.items():
        if hasattr(delivery, key):
            setattr(delivery, key, value)

    await db.flush()

    if new_status and new_status.value != before_status:
        await log_action(
            db,
            actor_user_id=actor_user_id,
            action_type="delivery.status_change",
            target_table="deliveries",
            target_id=str(delivery_id),
            before_data={"delivery_status": before_status},
            after_data={"delivery_status": new_status.value},
        )

    return delivery
