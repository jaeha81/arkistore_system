"""
발주 리포지토리
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PurchaseOrderStatus
from app.models.purchase_order import PurchaseOrder
from app.repositories.base import BaseRepository


class PurchaseOrderRepository(BaseRepository[PurchaseOrder]):
    model = PurchaseOrder

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        order_status: PurchaseOrderStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[PurchaseOrder], int]:
        stmt = select(PurchaseOrder)
        count_stmt = select(func.count()).select_from(PurchaseOrder)

        if order_status is not None:
            stmt = stmt.where(PurchaseOrder.order_status == order_status)
            count_stmt = count_stmt.where(PurchaseOrder.order_status == order_status)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(PurchaseOrder.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_idempotency_key(self, key: str) -> PurchaseOrder | None:
        stmt = select(PurchaseOrder).where(PurchaseOrder.idempotency_key == key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
