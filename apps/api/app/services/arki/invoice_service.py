"""
인보이스 관리 서비스 (업무 도메인)
"""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice


async def list_invoices(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[Invoice], int]:
    """인보이스 목록 조회"""
    stmt = select(Invoice)

    if purchase_order_id := filters.get("purchase_order_id"):
        stmt = stmt.where(Invoice.purchase_order_id == purchase_order_id)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(Invoice.invoice_date.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_invoice(
    data: dict[str, Any],
    db: AsyncSession,
) -> Invoice:
    """인보이스 생성"""
    invoice = Invoice(**data)
    db.add(invoice)
    await db.flush()
    return invoice
