"""
로그 조회 API 라우터 (운영 도메인)
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response
from app.services.ops import log_service

router = APIRouter(prefix="/ops/logs", tags=["Ops - Logs"])


@router.get("/events")
async def list_event_logs(
    request: Request,
    project_code: str | None = Query(None),
    event_type: str | None = Query(None),
    environment: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """이벤트 로그 목록 조회"""
    filters = {
        "project_code": project_code,
        "event_type": event_type,
        "environment": environment,
        "page": page,
        "page_size": page_size,
    }
    logs, total = await log_service.list_event_logs(filters, db)
    return paginated_response(
        data=[
            {
                "id": str(log.id),
                "project_code": log.project_code,
                "environment": log.environment.value if log.environment else None,
                "app_version": log.app_version,
                "event_type": log.event_type,
                "event_name": log.event_name,
                "payload": log.payload,
                "logged_at": log.logged_at.isoformat() if log.logged_at else None,
            }
            for log in logs
        ],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.get("/errors")
async def list_error_logs(
    request: Request,
    project_code: str | None = Query(None),
    error_code: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """에러 로그 목록 조회"""
    filters = {
        "project_code": project_code,
        "error_code": error_code,
        "status": status_filter,
        "page": page,
        "page_size": page_size,
    }
    logs, total = await log_service.list_error_logs(filters, db)
    return paginated_response(
        data=[
            {
                "id": str(log.id),
                "project_code": log.project_code,
                "error_code": log.error_code,
                "error_message_masked": log.error_message_masked,
                "report_status": log.report_status.value if log.report_status else None,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )
