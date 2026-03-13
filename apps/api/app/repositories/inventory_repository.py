"""
재고 리포지토리
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import InventoryStatus
from app.models.inventory import Inventory
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[Inventory]):
    model = Inventory

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        inventory_status: InventoryStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Inventory], int]:
        stmt = select(Inventory)
        count_stmt = select(func.count()).select_from(Inventory)

        if inventory_status is not None:
            stmt = stmt.where(Inventory.inventory_status == inventory_status)
            count_stmt = count_stmt.where(Inventory.inventory_status == inventory_status)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Inventory.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_product_id(self, product_id: UUID) -> Inventory | None:
        stmt = select(Inventory).where(Inventory.product_id == product_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
