"""
CAPA(배달 가용량) API 라우터 (업무 도메인)
"""
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import success_response
from app.services.arki import capacity_service

router = APIRouter(prefix="/arki/capacity-slots", tags=["Arki - Capacity Slots"])


@router.get("")
async def list_capacity_slots(
    request: Request,
    slot_date: date | None = Query(None),
    delivery_team: str | None = Query(None),
    slot_status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """CAPA 슬롯 목록 조회"""
    filters = {
        "slot_date": slot_date,
        "delivery_team": delivery_team,
        "slot_status": slot_status,
    }
    slots = await capacity_service.list_slots(filters, db)
    return success_response(
        data=[_serialize(s) for s in slots],
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_capacity_slot(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """CAPA 슬롯 생성"""
    body = await request.json()
    slot = await capacity_service.create_slot(body, db)
    return success_response(
        data=_serialize(slot),
        request_id=getattr(request.state, "request_id", None),
    )


@router.patch("/{slot_id}")
async def update_capacity_slot(
    slot_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """CAPA 슬롯 수정"""
    body = await request.json()
    slot = await capacity_service.update_slot(
        slot_id, body, db, current_user["id"]
    )
    return success_response(
        data=_serialize(slot),
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize(s) -> dict:
    return {
        "id": str(s.id),
        "slot_date": str(s.slot_date) if s.slot_date else None,
        "delivery_team": s.delivery_team,
        "time_slot": s.time_slot,
        "max_capacity": s.max_capacity,
        "used_capacity": s.used_capacity,
        "remaining_capacity": s.remaining_capacity,
        "slot_status": s.slot_status.value if s.slot_status else None,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }
