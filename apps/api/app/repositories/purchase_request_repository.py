"""
구매 요청 리포지토리
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PurchaseRequestStatus
from app.models.purchase_request import PurchaseRequest
from app.repositories.base import BaseRepository


class PurchaseRequestRepository(BaseRepository[PurchaseRequest]):
    model = PurchaseRequest

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        request_status: PurchaseRequestStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[PurchaseRequest], int]:
        stmt = select(PurchaseRequest)
        count_stmt = select(func.count()).select_from(PurchaseRequest)

        if request_status is not None:
            stmt = stmt.where(PurchaseRequest.request_status == request_status)
            count_stmt = count_stmt.where(PurchaseRequest.request_status == request_status)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(PurchaseRequest.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_idempotency_key(self, key: str) -> PurchaseRequest | None:
        stmt = select(PurchaseRequest).where(PurchaseRequest.idempotency_key == key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
