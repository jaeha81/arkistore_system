"""
인보이스 API 라우터 (업무 도메인)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.arki import invoice_service

router = APIRouter(prefix="/arki/invoices", tags=["Arki - Invoices"])


@router.get("")
async def list_invoices(
    request: Request,
    purchase_order_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """인보이스 목록 조회"""
    filters = {
        "purchase_order_id": purchase_order_id,
        "page": page,
        "page_size": page_size,
    }
    invoices, total = await invoice_service.list_invoices(filters, db)
    return paginated_response(
        data=[_serialize(inv) for inv in invoices],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_invoice(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """인보이스 생성"""
    body = await request.json()
    invoice = await invoice_service.create_invoice(body, db)
    return success_response(
        data=_serialize(invoice),
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize(inv) -> dict:
    return {
        "id": str(inv.id),
        "purchase_order_id": str(inv.purchase_order_id),
        "invoice_number": inv.invoice_number,
        "invoice_date": str(inv.invoice_date) if inv.invoice_date else None,
        "invoice_amount": float(inv.invoice_amount) if inv.invoice_amount else None,
        "currency": inv.currency,
        "file_attachment_id": str(inv.file_attachment_id) if inv.file_attachment_id else None,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
    }
