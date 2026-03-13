"""
상품 리포지토리
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    model = Product

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        q: str | None = None,
        brand_name: str | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Product], int]:
        stmt = select(Product).where(Product.deleted_at.is_(None))
        count_stmt = select(func.count()).select_from(Product).where(Product.deleted_at.is_(None))

        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(Product.product_name.ilike(pattern) | Product.product_code.ilike(pattern))
            count_stmt = count_stmt.where(Product.product_name.ilike(pattern) | Product.product_code.ilike(pattern))
        if brand_name is not None:
            stmt = stmt.where(Product.brand_name == brand_name)
            count_stmt = count_stmt.where(Product.brand_name == brand_name)
        if is_active is not None:
            stmt = stmt.where(Product.is_active.is_(is_active))
            count_stmt = count_stmt.where(Product.is_active.is_(is_active))

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Product.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_code(self, product_code: str) -> Product | None:
        stmt = select(Product).where(Product.product_code == product_code, Product.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
