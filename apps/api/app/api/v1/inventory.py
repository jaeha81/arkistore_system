"""
재고 관리 API 라우터 (업무 도메인)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.arki import inventory_service

router = APIRouter(prefix="/arki/inventory", tags=["Arki - Inventory"])


@router.get("")
async def list_inventory(
    request: Request,
    warehouse_name: str | None = Query(None),
    inventory_status: str | None = Query(None),
    product_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """재고 목록 조회"""
    filters = {
        "warehouse_name": warehouse_name,
        "inventory_status": inventory_status,
        "product_id": product_id,
        "page": page,
        "page_size": page_size,
    }
    items, total = await inventory_service.list_inventory(filters, db)
    return paginated_response(
        data=[_serialize(i) for i in items],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.patch("/{inventory_id}")
async def update_inventory(
    inventory_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """재고 수정"""
    body = await request.json()
    inv = await inventory_service.update_inventory(
        inventory_id, body, db, current_user["id"]
    )
    return success_response(
        data=_serialize(inv),
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize(i) -> dict:
    return {
        "id": str(i.id),
        "product_id": str(i.product_id),
        "warehouse_name": i.warehouse_name,
        "current_stock": float(i.current_stock),
        "reserved_stock": float(i.reserved_stock),
        "available_stock": float(i.available_stock),
        "safety_stock": float(i.safety_stock),
        "expected_inbound_date": str(i.expected_inbound_date) if i.expected_inbound_date else None,
        "inventory_status": i.inventory_status.value if i.inventory_status else None,
        "updated_at": i.updated_at.isoformat() if i.updated_at else None,
    }
