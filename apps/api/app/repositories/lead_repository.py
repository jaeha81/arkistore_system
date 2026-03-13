"""
리드(문의) 리포지토리
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import LeadStatus
from app.models.lead import Lead
from app.repositories.base import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    model = Lead

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        lead_status: LeadStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Lead], int]:
        stmt = select(Lead)
        count_stmt = select(func.count()).select_from(Lead)

        if lead_status is not None:
            stmt = stmt.where(Lead.lead_status == lead_status)
            count_stmt = count_stmt.where(Lead.lead_status == lead_status)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Lead.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total
