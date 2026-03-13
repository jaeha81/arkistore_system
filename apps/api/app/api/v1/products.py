"""
상품 관리 API 라우터 (업무 도메인)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.arki import product_service

router = APIRouter(prefix="/arki/products", tags=["Arki - Products"])


@router.get("")
async def list_products(
    request: Request,
    q: str | None = Query(None),
    category_name: str | None = Query(None),
    is_active: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """상품 목록 조회"""
    filters = {
        "q": q,
        "category_name": category_name,
        "is_active": is_active,
        "page": page,
        "page_size": page_size,
    }
    products, total = await product_service.list_products(filters, db)
    return paginated_response(
        data=[_serialize(p) for p in products],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_product(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """상품 생성"""
    body = await request.json()
    product = await product_service.create_product(body, db)
    return success_response(
        data=_serialize(product),
        request_id=getattr(request.state, "request_id", None),
    )


@router.patch("/{product_id}")
async def update_product(
    product_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """상품 수정"""
    body = await request.json()
    product = await product_service.update_product(product_id, body, db)
    return success_response(
        data=_serialize(product),
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize(p) -> dict:
    return {
        "id": str(p.id),
        "brand_name": p.brand_name,
        "product_code": p.product_code,
        "product_name": p.product_name,
        "category_name": p.category_name,
        "option_text": p.option_text,
        "unit_price": float(p.unit_price) if p.unit_price else None,
        "currency": p.currency,
        "supplier_name": p.supplier_name,
        "is_active": p.is_active,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }
