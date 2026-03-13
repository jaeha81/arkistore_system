"""
구매요청 관리 서비스 (업무 도메인)
"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PurchaseRequestStatus
from app.core.exceptions import (
    IdempotencyConflictException,
    InvalidStatusTransitionException,
    PurchaseRequestNotFoundException,
)
from app.models.purchase_request import PurchaseRequest
from app.services.audit_service import log_action

# 구매요청 상태 전이 규칙
STATUS_TRANSITIONS: dict[PurchaseRequestStatus, list[PurchaseRequestStatus]] = {
    PurchaseRequestStatus.requested: [
        PurchaseRequestStatus.reviewed,
        PurchaseRequestStatus.rejected,
    ],
    PurchaseRequestStatus.reviewed: [
        PurchaseRequestStatus.approved,
        PurchaseRequestStatus.rejected,
    ],
    PurchaseRequestStatus.approved: [
        PurchaseRequestStatus.converted_to_order,
    ],
    PurchaseRequestStatus.rejected: [],
    PurchaseRequestStatus.converted_to_order: [],
}


async def list_purchase_requests(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[PurchaseRequest], int]:
    """구매요청 목록 조회"""
    stmt = select(PurchaseRequest)

    if status := filters.get("request_status"):
        stmt = stmt.where(PurchaseRequest.request_status == status)
    if created_by := filters.get("created_by"):
        stmt = stmt.where(PurchaseRequest.created_by == created_by)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(PurchaseRequest.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_purchase_request(
    data: dict[str, Any],
    idempotency_key: str | None,
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> PurchaseRequest:
    """구매요청 생성 (멱등성 체크)"""
    if idempotency_key:
        existing = await db.execute(
            select(PurchaseRequest)
            .where(PurchaseRequest.idempotency_key == idempotency_key)
            .limit(1)
        )
        if existing.scalar_one_or_none():
            raise IdempotencyConflictException("Duplicate purchase request")

    pr = PurchaseRequest(
        **data,
        created_by=actor_user_id,
        idempotency_key=idempotency_key,
    )
    db.add(pr)
    await db.flush()
    return pr


async def update_purchase_request(
    request_id: uuid.UUID,
    data: dict[str, Any],
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> PurchaseRequest:
    """구매요청 수정 (상태 전이 검증, 승인/반려 감사 로그)"""
    stmt = select(PurchaseRequest).where(PurchaseRequest.id == request_id)
    result = await db.execute(stmt)
    pr = result.scalar_one_or_none()
    if not pr:
        raise PurchaseRequestNotFoundException()

    new_status = data.get("request_status")
    if new_status and new_status != pr.request_status:
        allowed = STATUS_TRANSITIONS.get(pr.request_status, [])
        if new_status not in allowed:
            raise InvalidStatusTransitionException(
                f"Cannot transition from {pr.request_status.value} to {new_status.value}"
            )

    before_status = pr.request_status.value

    for key, value in data.items():
        if hasattr(pr, key):
            setattr(pr, key, value)

    await db.flush()

    # 승인/반려 시 감사 로그
    if new_status and new_status in (
        PurchaseRequestStatus.approved,
        PurchaseRequestStatus.rejected,
    ):
        await log_action(
            db,
            actor_user_id=actor_user_id,
            action_type=f"purchase_request.{new_status.value}",
            target_table="purchase_requests",
            target_id=str(request_id),
            before_data={"request_status": before_status},
            after_data={"request_status": new_status.value},
        )

    return pr
