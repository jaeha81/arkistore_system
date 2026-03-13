"""
계약 관리 API 라우터 (업무 도메인)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.arki import contract_service

router = APIRouter(prefix="/arki/contracts", tags=["Arki - Contracts"])


@router.get("")
async def list_contracts(
    request: Request,
    contract_status: str | None = Query(None),
    customer_id: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """계약 목록 조회"""
    filters = {
        "contract_status": contract_status,
        "customer_id": customer_id,
        "page": page,
        "page_size": page_size,
    }
    contracts, total = await contract_service.list_contracts(filters, db)
    return paginated_response(
        data=[_serialize(c) for c in contracts],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_contract(
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """계약 생성"""
    body = await request.json()
    contract = await contract_service.create_contract(
        data=body,
        idempotency_key=idempotency_key,
        db=db,
        actor_user_id=current_user["id"],
    )
    return success_response(
        data=_serialize(contract),
        request_id=getattr(request.state, "request_id", None),
    )


@router.patch("/{contract_id}")
async def update_contract(
    contract_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """계약 수정"""
    body = await request.json()
    contract = await contract_service.update_contract(
        contract_id, body, db, current_user["id"]
    )
    return success_response(
        data=_serialize(contract),
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("/{contract_id}/attachments", status_code=status.HTTP_201_CREATED)
async def attach_file(
    contract_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """계약에 첨부파일 연결"""
    body = await request.json()
    await contract_service.attach_file(
        contract_id=contract_id,
        attachment_id=body["attachment_id"],
        attachment_type=body.get("attachment_type", "document"),
        notes=body.get("notes"),
        db=db,
    )
    return success_response(
        data={"message": "Attachment linked"},
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize(c) -> dict:
    return {
        "id": str(c.id),
        "contract_number": c.contract_number,
        "customer_id": str(c.customer_id),
        "consultation_id": str(c.consultation_id) if c.consultation_id else None,
        "contract_date": str(c.contract_date) if c.contract_date else None,
        "contract_amount": float(c.contract_amount) if c.contract_amount else None,
        "deposit_amount": float(c.deposit_amount) if c.deposit_amount else None,
        "contract_status": c.contract_status.value if c.contract_status else None,
        "delivery_required": c.delivery_required,
        "remarks": c.remarks,
        "created_by": str(c.created_by) if c.created_by else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
