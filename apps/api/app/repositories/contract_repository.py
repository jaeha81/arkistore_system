"""
계약 리포지토리
"""
from uuid import UUID

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ContractStatus
from app.models.contract import Contract
from app.repositories.base import BaseRepository


class ContractRepository(BaseRepository[Contract]):
    model = Contract

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        contract_status: ContractStatus | None = None,
        customer_id: UUID | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Contract], int]:
        stmt = select(Contract).where(Contract.deleted_at.is_(None))
        count_stmt = select(func.count()).select_from(Contract).where(Contract.deleted_at.is_(None))

        if contract_status is not None:
            stmt = stmt.where(Contract.contract_status == contract_status)
            count_stmt = count_stmt.where(Contract.contract_status == contract_status)
        if customer_id is not None:
            stmt = stmt.where(Contract.customer_id == customer_id)
            count_stmt = count_stmt.where(Contract.customer_id == customer_id)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Contract.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_active_by_id(self, id: UUID) -> Contract | None:
        stmt = select(Contract).where(Contract.id == id, Contract.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, key: str) -> Contract | None:
        stmt = select(Contract).where(Contract.idempotency_key == key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_max_sequence_for_month(self, year: int, month: int) -> int:
        """해당 월의 최대 계약번호 시퀀스를 반환한다 (계약번호 생성용)."""
        stmt = (
            select(func.count())
            .select_from(Contract)
            .where(
                extract("year", Contract.contract_date) == year,
                extract("month", Contract.contract_date) == month,
            )
        )
        result = (await self.db.execute(stmt)).scalar_one()
        return result
