"""
CAPA(배달 가용량) 관리 서비스 (업무 도메인)
"""
import uuid
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import SlotStatus
from app.core.exceptions import CapacityConflictException, NotFoundException
from app.models.capacity_slot import CapacitySlot
from app.services.audit_service import log_action


async def list_slots(
    filters: dict[str, Any],
    db: AsyncSession,
) -> list[CapacitySlot]:
    """CAPA 슬롯 목록 조회"""
    stmt = select(CapacitySlot)

    if slot_date := filters.get("slot_date"):
        stmt = stmt.where(CapacitySlot.slot_date == slot_date)
    if delivery_team := filters.get("delivery_team"):
        stmt = stmt.where(CapacitySlot.delivery_team == delivery_team)
    if slot_status := filters.get("slot_status"):
        stmt = stmt.where(CapacitySlot.slot_status == slot_status)

    stmt = stmt.order_by(CapacitySlot.slot_date, CapacitySlot.time_slot)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_slot(
    data: dict[str, Any],
    db: AsyncSession,
) -> CapacitySlot:
    """CAPA 슬롯 생성"""
    data["remaining_capacity"] = data["max_capacity"] - data.get("used_capacity", 0)
    slot = CapacitySlot(**data)
    db.add(slot)
    await db.flush()
    return slot


async def update_slot(
    slot_id: uuid.UUID,
    data: dict[str, Any],
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> CapacitySlot:
    """CAPA 슬롯 수정 + 감사 로그"""
    stmt = select(CapacitySlot).where(CapacitySlot.id == slot_id)
    result = await db.execute(stmt)
    slot = result.scalar_one_or_none()
    if not slot:
        raise NotFoundException("Capacity slot not found")

    before_data = {
        "max_capacity": slot.max_capacity,
        "used_capacity": slot.used_capacity,
        "slot_status": slot.slot_status.value,
    }

    for key, value in data.items():
        if hasattr(slot, key):
            setattr(slot, key, value)

    # remaining_capacity 재계산
    slot.remaining_capacity = slot.max_capacity - slot.used_capacity

    # 상태 자동 갱신
    if slot.remaining_capacity <= 0:
        slot.slot_status = SlotStatus.full
    elif slot.remaining_capacity <= slot.max_capacity * 0.2:
        slot.slot_status = SlotStatus.limited
    else:
        slot.slot_status = SlotStatus.open

    await db.flush()

    await log_action(
        db,
        actor_user_id=actor_user_id,
        action_type="capacity_slot.update",
        target_table="capacity_slots",
        target_id=str(slot_id),
        before_data=before_data,
        after_data={
            "max_capacity": slot.max_capacity,
            "used_capacity": slot.used_capacity,
            "remaining_capacity": slot.remaining_capacity,
            "slot_status": slot.slot_status.value,
        },
    )
    return slot


async def reserve_slot(
    slot_date: date,
    delivery_team: str,
    time_slot: str,
    db: AsyncSession,
) -> CapacitySlot:
    """CAPA 슬롯 예약 (배달 생성 시 호출)"""
    stmt = select(CapacitySlot).where(
        CapacitySlot.slot_date == slot_date,
        CapacitySlot.delivery_team == delivery_team,
        CapacitySlot.time_slot == time_slot,
    )
    result = await db.execute(stmt)
    slot = result.scalar_one_or_none()

    if not slot:
        raise CapacityConflictException("No capacity slot found for the given date/team/time")

    if slot.remaining_capacity <= 0 or slot.slot_status in (SlotStatus.full, SlotStatus.closed):
        raise CapacityConflictException("Delivery slot is full or unavailable")

    slot.used_capacity += 1
    slot.remaining_capacity = slot.max_capacity - slot.used_capacity

    if slot.remaining_capacity <= 0:
        slot.slot_status = SlotStatus.full
    elif slot.remaining_capacity <= slot.max_capacity * 0.2:
        slot.slot_status = SlotStatus.limited

    await db.flush()
    return slot


async def release_slot(
    slot_date: date,
    delivery_team: str,
    time_slot: str,
    db: AsyncSession,
) -> None:
    """CAPA 슬롯 해제 (배달 취소 시 호출)"""
    stmt = select(CapacitySlot).where(
        CapacitySlot.slot_date == slot_date,
        CapacitySlot.delivery_team == delivery_team,
        CapacitySlot.time_slot == time_slot,
    )
    result = await db.execute(stmt)
    slot = result.scalar_one_or_none()

    if slot and slot.used_capacity > 0:
        slot.used_capacity -= 1
        slot.remaining_capacity = slot.max_capacity - slot.used_capacity

        if slot.remaining_capacity > slot.max_capacity * 0.2:
            slot.slot_status = SlotStatus.open
        elif slot.remaining_capacity > 0:
            slot.slot_status = SlotStatus.limited

        await db.flush()
