"""
프로젝트 리포지토리
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import OperationMode, ProjectStatus
from app.models.project import Project
from app.models.project_site import ProjectSite
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    model = Project

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        status: ProjectStatus | None = None,
        operation_mode: OperationMode | None = None,
        q: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Project], int]:
        stmt = select(Project).where(Project.deleted_at.is_(None))
        count_stmt = select(func.count()).select_from(Project).where(Project.deleted_at.is_(None))

        if status is not None:
            stmt = stmt.where(Project.status == status)
            count_stmt = count_stmt.where(Project.status == status)
        if operation_mode is not None:
            stmt = stmt.where(Project.operation_mode == operation_mode)
            count_stmt = count_stmt.where(Project.operation_mode == operation_mode)
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(Project.name.ilike(pattern) | Project.project_code.ilike(pattern))
            count_stmt = count_stmt.where(Project.name.ilike(pattern) | Project.project_code.ilike(pattern))

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Project.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_code(self, project_code: str) -> Project | None:
        stmt = select(Project).where(Project.project_code == project_code, Project.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_active(self, id: UUID) -> Project | None:
        stmt = select(Project).where(Project.id == id, Project.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_site(self, site: ProjectSite) -> ProjectSite:
        self.db.add(site)
        await self.db.flush()
        await self.db.refresh(site)
        return site

    async def list_sites(self, project_id: UUID) -> list[ProjectSite]:
        stmt = select(ProjectSite).where(ProjectSite.project_id == project_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
