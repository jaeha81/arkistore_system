"""
고객 관리 API 라우터 (업무 도메인)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.arki import customer_service

router = APIRouter(prefix="/arki/customers", tags=["Arki - Customers"])


@router.get("")
async def list_customers(
    request: Request,
    q: str | None = Query(None),
    grade: str | None = Query(None),
    region: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """고객 목록 조회"""
    filters = {
        "q": q,
        "grade": grade,
        "region": region,
        "page": page,
        "page_size": page_size,
    }
    customers, total = await customer_service.list_customers(filters, db)
    return paginated_response(
        data=[_serialize(c) for c in customers],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_customer(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """고객 생성"""
    body = await request.json()
    customer = await customer_service.create_customer(body, db)
    return success_response(
        data=_serialize(customer),
        request_id=getattr(request.state, "request_id", None),
    )


@router.patch("/{customer_id}")
async def update_customer(
    customer_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """고객 수정"""
    body = await request.json()
    customer = await customer_service.update_customer(customer_id, body, db)
    return success_response(
        data=_serialize(customer),
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize(c) -> dict:
    return {
        "id": str(c.id),
        "customer_type": c.customer_type,
        "name": c.name,
        "phone_masked": c.phone_masked,
        "email_masked": c.email_masked,
        "region": c.region,
        "source_channel": c.source_channel,
        "grade": c.grade.value if c.grade else None,
        "is_vip": c.is_vip,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
