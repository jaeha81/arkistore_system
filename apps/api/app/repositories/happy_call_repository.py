"""
해피콜 리포지토리
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.happy_call import HappyCall
from app.repositories.base import BaseRepository


class HappyCallRepository(BaseRepository[HappyCall]):
    model = HappyCall

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        delivery_id: UUID | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[HappyCall], int]:
        stmt = select(HappyCall)
        count_stmt = select(func.count()).select_from(HappyCall)

        if delivery_id is not None:
            stmt = stmt.where(HappyCall.delivery_id == delivery_id)
            count_stmt = count_stmt.where(HappyCall.delivery_id == delivery_id)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(HappyCall.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total
