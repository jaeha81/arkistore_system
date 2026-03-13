"""
상품 관리 서비스 (업무 도메인)
"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ProductNotFoundException
from app.models.product import Product


async def list_products(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[Product], int]:
    """상품 목록 조회"""
    stmt = select(Product).where(Product.deleted_at.is_(None))

    if q := filters.get("q"):
        search = f"%{q}%"
        stmt = stmt.where(
            Product.product_name.ilike(search)
            | Product.product_code.ilike(search)
            | Product.brand_name.ilike(search)
        )
    if category := filters.get("category_name"):
        stmt = stmt.where(Product.category_name == category)
    if filters.get("is_active") is not None:
        stmt = stmt.where(Product.is_active == filters["is_active"])

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(Product.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_product(
    data: dict[str, Any],
    db: AsyncSession,
) -> Product:
    """상품 생성"""
    product = Product(**data)
    db.add(product)
    await db.flush()
    return product


async def update_product(
    product_id: uuid.UUID,
    data: dict[str, Any],
    db: AsyncSession,
) -> Product:
    """상품 수정"""
    stmt = select(Product).where(
        Product.id == product_id, Product.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise ProductNotFoundException()

    for key, value in data.items():
        if hasattr(product, key):
            setattr(product, key, value)

    await db.flush()
    return product
