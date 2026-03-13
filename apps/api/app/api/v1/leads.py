"""
리드(문의) 관리 API 라우터 (업무 도메인)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.arki import lead_service

router = APIRouter(prefix="/arki/leads", tags=["Arki - Leads"])


@router.get("")
async def list_leads(
    request: Request,
    lead_status: str | None = Query(None),
    lead_channel: str | None = Query(None),
    assigned_to: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """리드 목록 조회"""
    filters = {
        "lead_status": lead_status,
        "lead_channel": lead_channel,
        "assigned_to": assigned_to,
        "page": page,
        "page_size": page_size,
    }
    leads, total = await lead_service.list_leads(filters, db)
    return paginated_response(
        data=[_serialize(l) for l in leads],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_lead(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """리드 생성"""
    body = await request.json()
    lead = await lead_service.create_lead(body, db)
    return success_response(
        data=_serialize(lead),
        request_id=getattr(request.state, "request_id", None),
    )


@router.patch("/{lead_id}")
async def update_lead(
    lead_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """리드 수정"""
    body = await request.json()
    lead = await lead_service.update_lead(lead_id, body, db)
    return success_response(
        data=_serialize(lead),
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize(l) -> dict:
    return {
        "id": str(l.id),
        "customer_id": str(l.customer_id),
        "lead_channel": l.lead_channel,
        "inquiry_title": l.inquiry_title,
        "inquiry_content": l.inquiry_content,
        "assigned_to": str(l.assigned_to) if l.assigned_to else None,
        "lead_status": l.lead_status.value if l.lead_status else None,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    }
