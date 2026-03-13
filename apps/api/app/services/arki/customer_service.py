"""
고객 관리 서비스 (업무 도메인)
"""
import re
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CustomerNotFoundException
from app.models.customer import Customer


def _mask_phone(phone: str | None) -> str | None:
    """전화번호 마스킹: 010-1234-5678 → 010-****-5678"""
    if not phone:
        return None
    digits = re.sub(r"[^0-9]", "", phone)
    if len(digits) >= 8:
        return digits[:3] + "-****-" + digits[-4:]
    return "***"


def _mask_email(email: str | None) -> str | None:
    """이메일 마스킹: user@example.com → u***@example.com"""
    if not email:
        return None
    parts = email.split("@")
    if len(parts) == 2:
        local = parts[0]
        masked_local = local[0] + "***" if local else "***"
        return f"{masked_local}@{parts[1]}"
    return "***@***"


async def list_customers(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[Customer], int]:
    """고객 목록 조회"""
    stmt = select(Customer).where(Customer.deleted_at.is_(None))

    if q := filters.get("q"):
        search = f"%{q}%"
        stmt = stmt.where(
            Customer.name.ilike(search) | Customer.phone_masked.ilike(search)
        )
    if grade := filters.get("grade"):
        stmt = stmt.where(Customer.grade == grade)
    if region := filters.get("region"):
        stmt = stmt.where(Customer.region == region)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(Customer.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_customer(
    data: dict[str, Any],
    db: AsyncSession,
) -> Customer:
    """고객 생성 (전화번호/이메일 마스킹 후 저장)"""
    data["phone_masked"] = _mask_phone(data.get("phone"))
    data["email_masked"] = _mask_email(data.get("email"))

    customer = Customer(**data)
    db.add(customer)
    await db.flush()
    return customer


async def update_customer(
    customer_id: uuid.UUID,
    data: dict[str, Any],
    db: AsyncSession,
) -> Customer:
    """고객 수정"""
    stmt = select(Customer).where(
        Customer.id == customer_id, Customer.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    if not customer:
        raise CustomerNotFoundException()

    # 전화번호/이메일 변경 시 마스킹 갱신
    if "phone" in data:
        data["phone_masked"] = _mask_phone(data["phone"])
    if "email" in data:
        data["email_masked"] = _mask_email(data["email"])

    for key, value in data.items():
        if hasattr(customer, key):
            setattr(customer, key, value)

    await db.flush()
    return customer
