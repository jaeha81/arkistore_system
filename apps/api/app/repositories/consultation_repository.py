"""
상담 리포지토리
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.consultation import Consultation
from app.repositories.base import BaseRepository


class ConsultationRepository(BaseRepository[Consultation]):
    model = Consultation

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        customer_id: UUID | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Consultation], int]:
        stmt = select(Consultation)
        count_stmt = select(func.count()).select_from(Consultation)

        if customer_id is not None:
            stmt = stmt.where(Consultation.customer_id == customer_id)
            count_stmt = count_stmt.where(Consultation.customer_id == customer_id)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Consultation.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total
