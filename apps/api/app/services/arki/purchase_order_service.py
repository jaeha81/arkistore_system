"""
발주 관리 서비스 (업무 도메인)
"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PurchaseOrderStatus, PurchaseRequestStatus
from app.core.exceptions import (
    IdempotencyConflictException,
    InvalidStatusTransitionException,
    PurchaseOrderNotFoundException,
)
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.purchase_request import PurchaseRequest
from app.services.audit_service import log_action

# 발주 상태 전이 규칙
STATUS_TRANSITIONS: dict[PurchaseOrderStatus, list[PurchaseOrderStatus]] = {
    PurchaseOrderStatus.created: [
        PurchaseOrderStatus.ordered,
        PurchaseOrderStatus.cancelled,
    ],
    PurchaseOrderStatus.ordered: [
        PurchaseOrderStatus.invoiced,
        PurchaseOrderStatus.cancelled,
    ],
    PurchaseOrderStatus.invoiced: [
        PurchaseOrderStatus.shipped,
    ],
    PurchaseOrderStatus.shipped: [
        PurchaseOrderStatus.completed,
    ],
    PurchaseOrderStatus.completed: [],
    PurchaseOrderStatus.cancelled: [],
}


async def list_purchase_orders(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[PurchaseOrder], int]:
    """발주 목록 조회"""
    stmt = select(PurchaseOrder)

    if status := filters.get("order_status"):
        stmt = stmt.where(PurchaseOrder.order_status == status)
    if supplier := filters.get("supplier_name"):
        stmt = stmt.where(PurchaseOrder.supplier_name.ilike(f"%{supplier}%"))
    if payment_status := filters.get("payment_status"):
        stmt = stmt.where(PurchaseOrder.payment_status == payment_status)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(PurchaseOrder.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_purchase_order(
    data: dict[str, Any],
    idempotency_key: str | None,
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> PurchaseOrder:
    """
    발주 생성
    - items로부터 total_amount 계산
    - purchase_request_id 있으면 구매요청 상태를 converted_to_order로 변경
    """
    if idempotency_key:
        existing = await db.execute(
            select(PurchaseOrder)
            .where(PurchaseOrder.idempotency_key == idempotency_key)
            .limit(1)
        )
        if existing.scalar_one_or_none():
            raise IdempotencyConflictException("Duplicate purchase order")

    items_data = data.pop("items", [])

    # total_amount 계산
    total_amount = sum(
        float(item.get("ordered_qty", 0)) * float(item.get("unit_price", 0))
        for item in items_data
    )

    order = PurchaseOrder(
        **data,
        total_amount=total_amount,
        created_by=actor_user_id,
        idempotency_key=idempotency_key,
    )
    db.add(order)
    await db.flush()

    # 아이템 생성
    for item_data in items_data:
        line_total = float(item_data.get("ordered_qty", 0)) * float(item_data.get("unit_price", 0))
        item = PurchaseOrderItem(
            order_id=order.id,
            product_id=item_data["product_id"],
            ordered_qty=item_data["ordered_qty"],
            unit_price=item_data["unit_price"],
            line_total=line_total,
        )
        db.add(item)

    # 구매요청 상태 업데이트
    purchase_request_id = data.get("purchase_request_id")
    if purchase_request_id:
        pr_stmt = select(PurchaseRequest).where(PurchaseRequest.id == purchase_request_id)
        pr_result = await db.execute(pr_stmt)
        pr = pr_result.scalar_one_or_none()
        if pr:
            pr.request_status = PurchaseRequestStatus.converted_to_order

    await db.flush()
    return order


async def update_purchase_order(
    order_id: uuid.UUID,
    data: dict[str, Any],
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> PurchaseOrder:
    """발주 수정 (상태 전이 검증)"""
    stmt = select(PurchaseOrder).where(PurchaseOrder.id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if not order:
        raise PurchaseOrderNotFoundException()

    new_status = data.get("order_status")
    if new_status and new_status != order.order_status:
        allowed = STATUS_TRANSITIONS.get(order.order_status, [])
        if new_status not in allowed:
            raise InvalidStatusTransitionException(
                f"Cannot transition from {order.order_status.value} to {new_status.value}"
            )

    before_status = order.order_status.value

    for key, value in data.items():
        if hasattr(order, key):
            setattr(order, key, value)

    await db.flush()

    if new_status and new_status.value != before_status:
        await log_action(
            db,
            actor_user_id=actor_user_id,
            action_type="purchase_order.status_change",
            target_table="purchase_orders",
            target_id=str(order_id),
            before_data={"order_status": before_status},
            after_data={"order_status": new_status.value},
        )

    return order
