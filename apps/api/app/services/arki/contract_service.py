"""
계약 관리 서비스 (업무 도메인)
"""
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ContractStatus
from app.core.exceptions import (
    ContractNotFoundException,
    IdempotencyConflictException,
    InvalidStatusTransitionException,
    NotFoundException,
)
from app.models.attachment import Attachment
from app.models.contract import Contract
from app.services.audit_service import log_action

# 계약 상태 전이 규칙
STATUS_TRANSITIONS: dict[ContractStatus, list[ContractStatus]] = {
    ContractStatus.draft: [ContractStatus.signed, ContractStatus.cancelled],
    ContractStatus.signed: [ContractStatus.confirmed, ContractStatus.cancelled],
    ContractStatus.confirmed: [ContractStatus.cancelled],
    ContractStatus.cancelled: [],
}


async def _generate_contract_number(db: AsyncSession) -> str:
    """계약번호 생성: YYYYMM-XXXX"""
    now = datetime.now(timezone.utc)
    prefix = now.strftime("%Y%m")
    stmt = (
        select(func.count())
        .select_from(Contract)
        .where(Contract.contract_number.like(f"{prefix}-%"))
    )
    count = (await db.execute(stmt)).scalar() or 0
    seq = count + 1
    return f"{prefix}-{seq:04d}"


async def list_contracts(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[Contract], int]:
    """계약 목록 조회"""
    stmt = select(Contract).where(Contract.deleted_at.is_(None))

    if status := filters.get("contract_status"):
        stmt = stmt.where(Contract.contract_status == status)
    if customer_id := filters.get("customer_id"):
        stmt = stmt.where(Contract.customer_id == customer_id)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(Contract.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_contract(
    data: dict[str, Any],
    idempotency_key: str | None,
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> Contract:
    """계약 생성 (계약번호 자동 생성, 멱등성 체크)"""
    # Idempotency 체크
    if idempotency_key:
        existing = await db.execute(
            select(Contract).where(Contract.idempotency_key == idempotency_key).limit(1)
        )
        if existing.scalar_one_or_none():
            raise IdempotencyConflictException("Duplicate contract creation request")

    contract_number = await _generate_contract_number(db)
    contract = Contract(
        **data,
        contract_number=contract_number,
        created_by=actor_user_id,
        idempotency_key=idempotency_key,
    )
    db.add(contract)
    await db.flush()

    await log_action(
        db,
        actor_user_id=actor_user_id,
        action_type="contract.create",
        target_table="contracts",
        target_id=str(contract.id),
        after_data={"contract_number": contract_number, **data},
    )
    return contract


async def update_contract(
    contract_id: uuid.UUID,
    data: dict[str, Any],
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> Contract:
    """계약 수정 (상태 전이 검증)"""
    stmt = select(Contract).where(
        Contract.id == contract_id, Contract.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    contract = result.scalar_one_or_none()
    if not contract:
        raise ContractNotFoundException()

    # 상태 전이 검증
    new_status = data.get("contract_status")
    if new_status and new_status != contract.contract_status:
        allowed = STATUS_TRANSITIONS.get(contract.contract_status, [])
        if new_status not in allowed:
            raise InvalidStatusTransitionException(
                f"Cannot transition from {contract.contract_status.value} to {new_status.value}"
            )

    before_data = {
        "contract_status": contract.contract_status.value,
    }

    for key, value in data.items():
        if hasattr(contract, key):
            setattr(contract, key, value)

    await db.flush()

    # 상태 변경 시 감사 로그
    if new_status and new_status != before_data["contract_status"]:
        await log_action(
            db,
            actor_user_id=actor_user_id,
            action_type="contract.status_change",
            target_table="contracts",
            target_id=str(contract_id),
            before_data=before_data,
            after_data={"contract_status": new_status.value if hasattr(new_status, "value") else new_status},
        )

    return contract


async def attach_file(
    contract_id: uuid.UUID,
    attachment_id: uuid.UUID,
    attachment_type: str,
    notes: str | None,
    db: AsyncSession,
) -> None:
    """계약에 첨부파일 연결"""
    # 계약 존재 확인
    stmt = select(Contract).where(
        Contract.id == contract_id, Contract.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise ContractNotFoundException()

    # 첨부파일 업데이트
    att_stmt = select(Attachment).where(Attachment.id == attachment_id)
    att_result = await db.execute(att_stmt)
    attachment = att_result.scalar_one_or_none()
    if not attachment:
        raise NotFoundException("Attachment not found")

    attachment.related_table = "contracts"
    attachment.related_id = contract_id
    await db.flush()
