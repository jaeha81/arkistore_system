"""
에러 리포트 API 라우터
프론트엔드에서 런타임 에러를 보고하는 엔드포인트
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services import error_report_service

router = APIRouter(prefix="/error-reports", tags=["Error Reports"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_error_report(
    request: Request,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
):
    """
    에러 리포트 수집 (인증 불필요 - 클라이언트에서 직접 호출)
    - 멱등성 지원 (Idempotency-Key 헤더)
    - 자동 이슈 그룹핑
    - 민감정보 마스킹
    """
    body = await request.json()
    result = await error_report_service.create_error_report(
        data=body,
        idempotency_key=idempotency_key,
        db=db,
    )
    return success_response(
        data=result,
        request_id=getattr(request.state, "request_id", None),
    )


@router.get("/groups")
async def list_issue_groups(
    request: Request,
    project_code: str | None = Query(None),
    group_status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """이슈 그룹 목록 조회 (관리자용)"""
    from sqlalchemy import func, select

    from app.models.issue_group import IssueGroup

    stmt = select(IssueGroup)
    if project_code:
        stmt = stmt.where(IssueGroup.group_title.contains(project_code))
    if group_status:
        stmt = stmt.where(IssueGroup.group_status == group_status)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(IssueGroup.last_seen_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    groups = list(result.scalars().all())

    return paginated_response(
        data=[_serialize_group(g) for g in groups],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.patch("/groups/{group_id}/status")
async def update_group_status(
    group_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """이슈 그룹 상태 변경 (acknowledged / resolved)"""
    from sqlalchemy import select

    from app.models.issue_group import IssueGroup

    body = await request.json()
    stmt = select(IssueGroup).where(IssueGroup.id == group_id)
    result = await db.execute(stmt)
    group = result.scalar_one_or_none()
    if not group:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Issue group not found")

    if new_status := body.get("group_status"):
        group.group_status = new_status
    await db.flush()

    return success_response(
        data=_serialize_group(group),
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize_group(g) -> dict:
    return {
        "id": str(g.id),
        "group_key": g.group_key,
        "group_title": g.group_title,
        "occurrence_count": g.occurrence_count,
        "group_status": g.group_status.value if hasattr(g.group_status, "value") else g.group_status,
        "first_seen_at": g.first_seen_at.isoformat() if g.first_seen_at else None,
        "last_seen_at": g.last_seen_at.isoformat() if g.last_seen_at else None,
    }
