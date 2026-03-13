"""
인보이스 리포지토리
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice
from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    model = Invoice

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        purchase_order_id: UUID | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Invoice], int]:
        stmt = select(Invoice)
        count_stmt = select(func.count()).select_from(Invoice)

        if purchase_order_id is not None:
            stmt = stmt.where(Invoice.purchase_order_id == purchase_order_id)
            count_stmt = count_stmt.where(Invoice.purchase_order_id == purchase_order_id)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Invoice.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total
