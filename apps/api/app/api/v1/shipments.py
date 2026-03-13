"""
배송(선적) API 라우터 (업무 도메인)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.arki import shipment_service

router = APIRouter(prefix="/arki/shipments", tags=["Arki - Shipments"])


@router.get("")
async def list_shipments(
    request: Request,
    purchase_order_id: UUID | None = Query(None),
    shipment_status: str | None = Query(None),
    customs_status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """배송 목록 조회"""
    filters = {
        "purchase_order_id": purchase_order_id,
        "shipment_status": shipment_status,
        "customs_status": customs_status,
        "page": page,
        "page_size": page_size,
    }
    shipments, total = await shipment_service.list_shipments(filters, db)
    return paginated_response(
        data=[_serialize(s) for s in shipments],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_shipment(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """배송 생성"""
    body = await request.json()
    shipment = await shipment_service.create_shipment(body, db)
    return success_response(
        data=_serialize(shipment),
        request_id=getattr(request.state, "request_id", None),
    )


@router.patch("/{shipment_id}")
async def update_shipment(
    shipment_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """배송 수정"""
    body = await request.json()
    shipment = await shipment_service.update_shipment(shipment_id, body, db)
    return success_response(
        data=_serialize(shipment),
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize(s) -> dict:
    return {
        "id": str(s.id),
        "purchase_order_id": str(s.purchase_order_id),
        "bl_number": s.bl_number,
        "shipping_company": s.shipping_company,
        "departure_date": str(s.departure_date) if s.departure_date else None,
        "estimated_arrival_date": str(s.estimated_arrival_date) if s.estimated_arrival_date else None,
        "actual_arrival_date": str(s.actual_arrival_date) if s.actual_arrival_date else None,
        "customs_status": s.customs_status,
        "shipment_status": s.shipment_status,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }
