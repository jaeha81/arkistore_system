"""
해피콜 API 라우터 (업무 도메인)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.arki import happy_call_service

router = APIRouter(prefix="/arki/happy-calls", tags=["Arki - Happy Calls"])


@router.get("")
async def list_happy_calls(
    request: Request,
    delivery_id: UUID | None = Query(None),
    call_result: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """해피콜 목록 조회"""
    filters = {
        "delivery_id": delivery_id,
        "call_result": call_result,
        "page": page,
        "page_size": page_size,
    }
    calls, total = await happy_call_service.list_happy_calls(filters, db)
    return paginated_response(
        data=[_serialize(hc) for hc in calls],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_happy_call(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """해피콜 생성"""
    body = await request.json()
    hc = await happy_call_service.create_happy_call(
        body, db, current_user["id"]
    )
    return success_response(
        data=_serialize(hc),
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize(hc) -> dict:
    return {
        "id": str(hc.id),
        "delivery_id": str(hc.delivery_id),
        "call_date": hc.call_date.isoformat() if hc.call_date else None,
        "address_confirmed": hc.address_confirmed,
        "ladder_confirmed": hc.ladder_confirmed,
        "contact_confirmed": hc.contact_confirmed,
        "special_notes": hc.special_notes,
        "call_result": hc.call_result,
        "created_by": str(hc.created_by) if hc.created_by else None,
        "created_at": hc.created_at.isoformat() if hc.created_at else None,
    }
