"""
배송 캐파 슬롯 리포지토리
"""
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import SlotStatus
from app.models.capacity_slot import CapacitySlot
from app.repositories.base import BaseRepository


class CapacitySlotRepository(BaseRepository[CapacitySlot]):
    model = CapacitySlot

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        slot_date: date | None = None,
        delivery_team: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[CapacitySlot]:
        stmt = select(CapacitySlot)

        if slot_date is not None:
            stmt = stmt.where(CapacitySlot.slot_date == slot_date)
        if delivery_team is not None:
            stmt = stmt.where(CapacitySlot.delivery_team == delivery_team)

        stmt = stmt.order_by(CapacitySlot.slot_date, CapacitySlot.time_slot).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_slot(
        self,
        slot_date: date,
        delivery_team: str,
        time_slot: str,
    ) -> CapacitySlot | None:
        stmt = select(CapacitySlot).where(
            CapacitySlot.slot_date == slot_date,
            CapacitySlot.delivery_team == delivery_team,
            CapacitySlot.time_slot == time_slot,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def reserve_slot(self, slot: CapacitySlot) -> CapacitySlot:
        """슬롯 1건 예약: used +1, remaining -1, 상태 갱신."""
        slot.used_capacity += 1
        slot.remaining_capacity -= 1
        if slot.remaining_capacity <= 0:
            slot.slot_status = SlotStatus.full
        elif slot.remaining_capacity <= slot.max_capacity * 0.2:
            slot.slot_status = SlotStatus.limited
        await self.db.flush()
        await self.db.refresh(slot)
        return slot
