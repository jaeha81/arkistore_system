"""
상담 관리 API 라우터 (업무 도메인)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.arki import consultation_service

router = APIRouter(prefix="/arki/consultations", tags=["Arki - Consultations"])


@router.get("")
async def list_consultations(
    request: Request,
    customer_id: UUID | None = Query(None),
    consultation_type: str | None = Query(None),
    manager_user_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """상담 목록 조회"""
    filters = {
        "customer_id": customer_id,
        "consultation_type": consultation_type,
        "manager_user_id": manager_user_id,
        "page": page,
        "page_size": page_size,
    }
    consultations, total = await consultation_service.list_consultations(filters, db)
    return paginated_response(
        data=[_serialize(c) for c in consultations],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_consultation(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """상담 생성"""
    body = await request.json()
    consultation = await consultation_service.create_consultation(body, db)
    return success_response(
        data=_serialize(consultation),
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize(c) -> dict:
    return {
        "id": str(c.id),
        "customer_id": str(c.customer_id),
        "manager_user_id": str(c.manager_user_id),
        "consultation_type": c.consultation_type,
        "summary": c.summary,
        "needs_text": c.needs_text,
        "next_action": c.next_action,
        "consultation_date": c.consultation_date.isoformat() if c.consultation_date else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
