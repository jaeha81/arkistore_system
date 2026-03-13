"""
배송 리포지토리
"""
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import DeliveryStatus
from app.models.delivery import Delivery
from app.repositories.base import BaseRepository


class DeliveryRepository(BaseRepository[Delivery]):
    model = Delivery

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        delivery_date: date | None = None,
        delivery_status: DeliveryStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Delivery], int]:
        stmt = select(Delivery)
        count_stmt = select(func.count()).select_from(Delivery)

        if delivery_date is not None:
            stmt = stmt.where(Delivery.delivery_date == delivery_date)
            count_stmt = count_stmt.where(Delivery.delivery_date == delivery_date)
        if delivery_status is not None:
            stmt = stmt.where(Delivery.delivery_status == delivery_status)
            count_stmt = count_stmt.where(Delivery.delivery_status == delivery_status)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Delivery.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_idempotency_key(self, key: str) -> Delivery | None:
        stmt = select(Delivery).where(Delivery.idempotency_key == key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
