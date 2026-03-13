"""
고객 리포지토리
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import CustomerGrade
from app.models.customer import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    model = Customer

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        q: str | None = None,
        grade: CustomerGrade | None = None,
        is_vip: bool | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Customer], int]:
        stmt = select(Customer).where(Customer.deleted_at.is_(None))
        count_stmt = select(func.count()).select_from(Customer).where(Customer.deleted_at.is_(None))

        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(Customer.name.ilike(pattern))
            count_stmt = count_stmt.where(Customer.name.ilike(pattern))
        if grade is not None:
            stmt = stmt.where(Customer.grade == grade)
            count_stmt = count_stmt.where(Customer.grade == grade)
        if is_vip is not None:
            stmt = stmt.where(Customer.is_vip.is_(is_vip))
            count_stmt = count_stmt.where(Customer.is_vip.is_(is_vip))

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Customer.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_active_by_id(self, id: UUID) -> Customer | None:
        stmt = select(Customer).where(Customer.id == id, Customer.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
