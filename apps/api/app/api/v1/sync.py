"""
시트 동기화 API 라우터
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import success_response
from app.services import sync_service

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.post("/sheets/export", status_code=status.HTTP_202_ACCEPTED)
async def create_export_job(
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """시트 내보내기 작업 생성 (비동기)"""
    body = await request.json()
    job = await sync_service.create_export_job(
        data=body,
        idempotency_key=idempotency_key,
        db=db,
        actor_user_id=current_user["id"],
    )
    return success_response(
        data={
            "job_id": str(job.id),
            "job_status": job.job_status,
        },
        request_id=getattr(request.state, "request_id", None),
    )


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """작업 상태 조회"""
    job = await sync_service.get_job_status(job_id, db)
    return success_response(
        data={
            "job_id": str(job.id),
            "job_type": job.job_type,
            "target_table": job.target_table,
            "job_status": job.job_status,
            "result_url": job.result_url,
            "error_message": job.error_message,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        },
        request_id=getattr(request.state, "request_id", None),
    )
