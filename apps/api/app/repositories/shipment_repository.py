"""
선적 리포지토리
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shipment import Shipment
from app.repositories.base import BaseRepository


class ShipmentRepository(BaseRepository[Shipment]):
    model = Shipment

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Shipment], int]:
        stmt = select(Shipment)
        count_stmt = select(func.count()).select_from(Shipment)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Shipment.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total
