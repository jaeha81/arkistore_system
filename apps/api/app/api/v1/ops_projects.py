"""
프로젝트 관리 API 라우터 (운영 도메인)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.responses import paginated_response, success_response
from app.services.ops import project_service

router = APIRouter(prefix="/ops/projects", tags=["Ops - Projects"])


@router.get("")
async def list_projects(
    request: Request,
    status_filter: str | None = Query(None, alias="status"),
    operation_mode: str | None = Query(None),
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """프로젝트 목록 조회"""
    filters = {
        "status": status_filter,
        "operation_mode": operation_mode,
        "q": q,
        "page": page,
        "page_size": page_size,
    }
    projects, total = await project_service.list_projects(filters, db)
    return paginated_response(
        data=[_serialize_project(p) for p in projects],
        page=page,
        page_size=page_size,
        total=total,
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """프로젝트 생성"""
    body = await request.json()
    project = await project_service.create_project(body, db, current_user["id"])
    return success_response(
        data=_serialize_project(project),
        request_id=getattr(request.state, "request_id", None),
    )


@router.get("/{project_id}")
async def get_project(
    project_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """프로젝트 단건 조회"""
    project = await project_service.get_project(project_id, db)
    return success_response(
        data=_serialize_project(project),
        request_id=getattr(request.state, "request_id", None),
    )


@router.patch("/{project_id}")
async def update_project(
    project_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """프로젝트 수정"""
    body = await request.json()
    project = await project_service.update_project(project_id, body, db, current_user["id"])
    return success_response(
        data=_serialize_project(project),
        request_id=getattr(request.state, "request_id", None),
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """프로젝트 소프트 삭제"""
    await project_service.soft_delete_project(project_id, db, current_user["id"])


@router.get("/{project_id}/sites")
async def list_project_sites(
    project_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """프로젝트 사이트 목록"""
    sites = await project_service.list_project_sites(project_id, db)
    return success_response(
        data=[
            {
                "id": str(s.id),
                "project_id": str(s.project_id),
                "site_code": s.site_code,
                "site_name": s.site_name,
                "site_url": s.site_url,
                "site_type": s.site_type.value if s.site_type else None,
                "is_enabled": s.is_enabled,
            }
            for s in sites
        ],
        request_id=getattr(request.state, "request_id", None),
    )


@router.post("/{project_id}/sites", status_code=status.HTTP_201_CREATED)
async def create_project_site(
    project_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """프로젝트 사이트 추가"""
    body = await request.json()
    site = await project_service.create_project_site(project_id, body, db)
    return success_response(
        data={
            "id": str(site.id),
            "project_id": str(site.project_id),
            "site_code": site.site_code,
            "site_name": site.site_name,
            "site_url": site.site_url,
            "site_type": site.site_type.value if site.site_type else None,
            "is_enabled": site.is_enabled,
        },
        request_id=getattr(request.state, "request_id", None),
    )


def _serialize_project(p) -> dict:
    return {
        "id": str(p.id),
        "project_code": p.project_code,
        "name": p.name,
        "client_name": p.client_name,
        "service_type": p.service_type,
        "main_url": p.main_url,
        "status": p.status.value if p.status else None,
        "operation_mode": p.operation_mode.value if p.operation_mode else None,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }
