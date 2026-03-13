"""
이슈/에러 리포트 API 라우터 (운영 도메인)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.ops import issue_service
from app.services import error_report_service

router = APIRouter(tags=["Ops - Issues"])


# ==================== Error Reports (에러 리포트) ====================

@router.get("/ops/issues")
async def list_issues(
    request: Request,
    project_code: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    error_code: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """에러 리포트 목록 조회"""
    filters = {
        "project_code": project_code,
        "status": status_filter,
        "error_code": error_code,
        "page": page,
        "page_size": page_size,
    }
    issues, total = await issue_service.list_issues(filters, db)
    return paginated_response(
        data=[_serialize_issue(i) for i in issues],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.get("/ops/issues/{issue_id}")
async def get_issue(
    issue_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """에러 리포트 단건 조회"""
    issue = await issue_service.get_issue(issue_id, db)
    return success_response(
        data=_serialize_issue(issue),
        request_id=getattr(request.state, "request_id", None),
    )


@router.patch("/ops/issues/{issue_id}/status")
async def update_issue_status(
    issue_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """에러 리포트 상태 변경"""
    body = await request.json()
    issue = await issue_service.update_issue_status(
        issue_id=issue_id,
        status=body["status"],
        reason=body.get("reason"),
        db=db,
        actor_user_id=current_user["id"],
    )
    return success_response(
        data=_serialize_issue(issue),
        request_id=getattr(request.state, "request_id", None),
    )


# ==================== Issue Groups ====================

@router.get("/ops/issue-groups")
async def list_issue_groups(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """이슈 그룹 목록 조회"""
    groups, total = await issue_service.list_issue_groups(skip, limit, db)
    return paginated_response(
        data=[
            {
                "id": str(g.id),
                "group_key": g.group_key,
                "group_title": g.group_title,
                "occurrence_count": g.occurrence_count,
                "first_seen_at": g.first_seen_at.isoformat() if g.first_seen_at else None,
                "last_seen_at": g.last_seen_at.isoformat() if g.last_seen_at else None,
                "group_status": g.group_status.value if g.group_status else None,
                "github_issue_id": str(g.github_issue_id) if g.github_issue_id else None,
            }
            for g in groups
        ],
        page=(skip // limit) + 1 if limit else 1,
        page_size=limit,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post(
    "/ops/issue-groups/{group_id}/github-issue",
    status_code=status.HTTP_201_CREATED,
)
async def create_github_issue(
    group_id: UUID,
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """이슈 그룹 → GitHub Issue 생성"""
    body = await request.json()
    result = await issue_service.create_github_issue(
        group_id=group_id,
        repository=body["repository"],
        labels=body.get("labels"),
        db=db,
        actor_user_id=current_user["id"],
    )
    return success_response(
        data=result,
        request_id=getattr(request.state, "request_id", None),
    )


# ==================== Error Reports (외부 수집) ====================

@router.post(
    "/ops/error-reports",
    status_code=status.HTTP_201_CREATED,
)
async def create_error_report(
    request: Request,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
):
    """에러 리포트 수집 (인증 불필요)"""
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


def _serialize_issue(i) -> dict:
    return {
        "id": str(i.id),
        "project_code": i.project_code,
        "site_type": i.site_type.value if i.site_type else None,
        "environment": i.environment.value if i.environment else None,
        "app_version": i.app_version,
        "screen_name": i.screen_name,
        "error_code": i.error_code,
        "error_message_masked": i.error_message_masked,
        "report_status": i.report_status.value if i.report_status else None,
        "issue_group_id": str(i.issue_group_id) if i.issue_group_id else None,
        "trace_id": i.trace_id,
        "occurred_at": i.occurred_at.isoformat() if i.occurred_at else None,
        "created_at": i.created_at.isoformat() if i.created_at else None,
    }
