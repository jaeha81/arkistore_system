"""
발주 관리 API 라우터 (업무 도메인)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.arki import purchase_order_service

router = APIRouter(prefix="/arki/purchase-orders", tags=["Arki - Purchase Orders"])


@router.get("")
async def list_purchase_orders(
    request: Request,
    order_status: str | None = Query(None),
    supplier_name: str | None = Query(None),
    payment_status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """발주 목록 조회"""
    filters = {
        "order_status": order_status,
        "supplier_name": supplier_name,
        "payment_status": payment_status,
        "page": page,
        "page_size": page_size,
    }
    orders, total = await purchase_order_service.list_purchase_orders(filters, db)
    return paginated_response(
        data=[_serialize(o) for o in orders],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """발주 생성"""
    body = await request.json()
    order = await purchase_order_service.create_purchase_order(
        data=body,
        idempotency_key=idempotency_key,
        db=db,
        actor_user_id=current_user["id"],
    )
    return success_response(
        data=_serialize(order),
        request_id=getattr(request.state, "request_id", None),
    )


@router.patch("/{order_id}")
async def update_purchase_order(
    order_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """발주 수정"""
    body = await request.json()
    order = await purchase_order_service.update_purchase_order(
        order_id, body, db, current_user["id"]
    )
    return success_response(
        data=_serialize(order),
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize(o) -> dict:
    return {
        "id": str(o.id),
        "order_number": o.order_number,
        "purchase_request_id": str(o.purchase_request_id) if o.purchase_request_id else None,
        "supplier_name": o.supplier_name,
        "order_date": str(o.order_date) if o.order_date else None,
        "currency": o.currency,
        "total_amount": float(o.total_amount) if o.total_amount else None,
        "payment_status": o.payment_status.value if o.payment_status else None,
        "order_status": o.order_status.value if o.order_status else None,
        "created_by": str(o.created_by) if o.created_by else None,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }
