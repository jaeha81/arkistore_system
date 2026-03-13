"""
구매요청 API 라우터 (업무 도메인)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.arki import purchase_request_service

router = APIRouter(prefix="/arki/purchase-requests", tags=["Arki - Purchase Requests"])


@router.get("")
async def list_purchase_requests(
    request: Request,
    request_status: str | None = Query(None),
    created_by: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """구매요청 목록 조회"""
    filters = {
        "request_status": request_status,
        "created_by": created_by,
        "page": page,
        "page_size": page_size,
    }
    prs, total = await purchase_request_service.list_purchase_requests(filters, db)
    return paginated_response(
        data=[_serialize(pr) for pr in prs],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_purchase_request(
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """구매요청 생성"""
    body = await request.json()
    pr = await purchase_request_service.create_purchase_request(
        data=body,
        idempotency_key=idempotency_key,
        db=db,
        actor_user_id=current_user["id"],
    )
    return success_response(
        data=_serialize(pr),
        request_id=getattr(request.state, "request_id", None),
    )


@router.patch("/{request_id}")
async def update_purchase_request(
    request_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """구매요청 수정"""
    body = await request.json()
    pr = await purchase_request_service.update_purchase_request(
        request_id, body, db, current_user["id"]
    )
    return success_response(
        data=_serialize(pr),
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize(pr) -> dict:
    return {
        "id": str(pr.id),
        "request_number": pr.request_number,
        "request_source": pr.request_source,
        "request_status": pr.request_status.value if pr.request_status else None,
        "required_date": str(pr.required_date) if pr.required_date else None,
        "reason_text": pr.reason_text,
        "created_by": str(pr.created_by) if pr.created_by else None,
        "created_at": pr.created_at.isoformat() if pr.created_at else None,
    }
