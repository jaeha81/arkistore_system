"""
대시보드 API 라우터 (업무 도메인)
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import success_response
from app.services.arki import dashboard_service

router = APIRouter(prefix="/arki/dashboard", tags=["Arki - Dashboard"])


@router.get("/summary")
async def get_summary(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """대시보드 요약 데이터"""
    summary = await dashboard_service.get_summary(db)
    return success_response(
        data=summary,
        request_id=getattr(request.state, "request_id", None),
    )
