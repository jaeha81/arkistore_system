"""
재고 관리 서비스 (업무 도메인)
"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import InventoryStatus
from app.core.exceptions import NotFoundException
from app.models.inventory import Inventory
from app.services.audit_service import log_action


async def list_inventory(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[Inventory], int]:
    """재고 목록 조회"""
    stmt = select(Inventory)

    if warehouse := filters.get("warehouse_name"):
        stmt = stmt.where(Inventory.warehouse_name == warehouse)
    if status := filters.get("inventory_status"):
        stmt = stmt.where(Inventory.inventory_status == status)
    if product_id := filters.get("product_id"):
        stmt = stmt.where(Inventory.product_id == product_id)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(Inventory.updated_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def update_inventory(
    inventory_id: uuid.UUID,
    data: dict[str, Any],
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> Inventory:
    """
    재고 수정
    - available_stock 재계산: current_stock - reserved_stock
    - safety_stock 대비 inventory_status 자동 갱신
    """
    stmt = select(Inventory).where(Inventory.id == inventory_id)
    result = await db.execute(stmt)
    inventory = result.scalar_one_or_none()
    if not inventory:
        raise NotFoundException("Inventory not found")

    before_data = {
        "current_stock": float(inventory.current_stock),
        "reserved_stock": float(inventory.reserved_stock),
        "inventory_status": inventory.inventory_status.value,
    }

    for key, value in data.items():
        if hasattr(inventory, key):
            setattr(inventory, key, value)

    # available_stock 재계산
    inventory.available_stock = float(inventory.current_stock) - float(inventory.reserved_stock)

    # inventory_status 자동 갱신
    if inventory.available_stock <= 0:
        inventory.inventory_status = InventoryStatus.out_of_stock
    elif float(inventory.available_stock) <= float(inventory.safety_stock):
        inventory.inventory_status = InventoryStatus.low_stock
    else:
        inventory.inventory_status = InventoryStatus.normal

    await db.flush()

    await log_action(
        db,
        actor_user_id=actor_user_id,
        action_type="inventory.update",
        target_table="inventories",
        target_id=str(inventory_id),
        before_data=before_data,
        after_data={
            "current_stock": float(inventory.current_stock),
            "reserved_stock": float(inventory.reserved_stock),
            "available_stock": float(inventory.available_stock),
            "inventory_status": inventory.inventory_status.value,
        },
    )
    return inventory
