"""
배달(납품) API 라우터 (업무 도메인)
"""
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.arki import delivery_service

router = APIRouter(prefix="/arki/deliveries", tags=["Arki - Deliveries"])


@router.get("")
async def list_deliveries(
    request: Request,
    delivery_date: date | None = Query(None),
    delivery_team: str | None = Query(None),
    delivery_status: str | None = Query(None),
    contract_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """배달 목록 조회"""
    filters = {
        "delivery_date": delivery_date,
        "delivery_team": delivery_team,
        "delivery_status": delivery_status,
        "contract_id": contract_id,
        "page": page,
        "page_size": page_size,
    }
    deliveries, total = await delivery_service.list_deliveries(filters, db)
    return paginated_response(
        data=[_serialize(d) for d in deliveries],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_delivery(
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """배달 생성"""
    body = await request.json()
    delivery = await delivery_service.create_delivery(
        data=body,
        idempotency_key=idempotency_key,
        db=db,
        actor_user_id=current_user["id"],
    )
    return success_response(
        data=_serialize(delivery),
        request_id=getattr(request.state, "request_id", None),
    )


@router.patch("/{delivery_id}")
async def update_delivery(
    delivery_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """배달 수정"""
    body = await request.json()
    delivery = await delivery_service.update_delivery(
        delivery_id, body, db, current_user["id"]
    )
    return success_response(
        data=_serialize(delivery),
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize(d) -> dict:
    return {
        "id": str(d.id),
        "delivery_number": d.delivery_number,
        "contract_id": str(d.contract_id),
        "customer_id": str(d.customer_id),
        "delivery_date": str(d.delivery_date) if d.delivery_date else None,
        "time_slot": d.time_slot,
        "delivery_team": d.delivery_team,
        "vehicle_code": d.vehicle_code,
        "address_text": d.address_text,
        "ladder_required": d.ladder_required,
        "delivery_status": d.delivery_status.value if d.delivery_status else None,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }
