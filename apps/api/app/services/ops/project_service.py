"""
프로젝트 관리 서비스 (운영 도메인)
"""
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import OperationMode, ProjectStatus
from app.core.exceptions import ProjectNotFoundException
from app.models.project import Project
from app.models.project_site import ProjectSite
from app.services.audit_service import log_action


async def list_projects(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[Project], int]:
    """프로젝트 목록 조회 (필터, 페이징)"""
    stmt = select(Project).where(Project.deleted_at.is_(None))

    # 필터 적용
    if status := filters.get("status"):
        stmt = stmt.where(Project.status == status)
    if operation_mode := filters.get("operation_mode"):
        stmt = stmt.where(Project.operation_mode == operation_mode)
    if q := filters.get("q"):
        search = f"%{q}%"
        stmt = stmt.where(
            Project.name.ilike(search) | Project.project_code.ilike(search)
        )

    # 전체 건수
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # 페이징
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(Project.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession,
) -> Project:
    """프로젝트 단건 조회"""
    stmt = (
        select(Project)
        .options(selectinload(Project.sites))
        .where(Project.id == project_id, Project.deleted_at.is_(None))
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise ProjectNotFoundException()
    return project


async def create_project(
    data: dict[str, Any],
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> Project:
    """프로젝트 생성 + 감사 로그"""
    project = Project(**data)
    db.add(project)
    await db.flush()

    await log_action(
        db,
        actor_user_id=actor_user_id,
        action_type="project.create",
        target_table="projects",
        target_id=str(project.id),
        after_data=data,
    )
    return project


async def update_project(
    project_id: uuid.UUID,
    data: dict[str, Any],
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> Project:
    """프로젝트 수정 + 감사 로그"""
    project = await get_project(project_id, db)

    before_data = {
        "name": project.name,
        "status": project.status.value if project.status else None,
        "operation_mode": project.operation_mode.value if project.operation_mode else None,
    }

    for key, value in data.items():
        if hasattr(project, key):
            setattr(project, key, value)

    await db.flush()

    await log_action(
        db,
        actor_user_id=actor_user_id,
        action_type="project.update",
        target_table="projects",
        target_id=str(project_id),
        before_data=before_data,
        after_data=data,
    )
    return project


async def soft_delete_project(
    project_id: uuid.UUID,
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> None:
    """프로젝트 소프트 삭제 + 감사 로그"""
    project = await get_project(project_id, db)
    project.deleted_at = datetime.now(timezone.utc)
    await db.flush()

    await log_action(
        db,
        actor_user_id=actor_user_id,
        action_type="project.delete",
        target_table="projects",
        target_id=str(project_id),
    )


async def list_project_sites(
    project_id: uuid.UUID,
    db: AsyncSession,
) -> list[ProjectSite]:
    """프로젝트 사이트 목록"""
    # 프로젝트 존재 확인
    await get_project(project_id, db)
    stmt = select(ProjectSite).where(ProjectSite.project_id == project_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_project_site(
    project_id: uuid.UUID,
    data: dict[str, Any],
    db: AsyncSession,
) -> ProjectSite:
    """프로젝트 사이트 추가"""
    await get_project(project_id, db)
    site = ProjectSite(project_id=project_id, **data)
    db.add(site)
    await db.flush()
    return site
