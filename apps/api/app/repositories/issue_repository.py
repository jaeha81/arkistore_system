"""
이슈 / 에러 리포트 리포지토리
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import Environment, IssueStatus, SiteType
from app.models.error_report import ErrorReport
from app.models.issue_group import IssueGroup
from app.repositories.base import BaseRepository


class IssueRepository(BaseRepository[ErrorReport]):
    model = ErrorReport

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        project_code: str | None = None,
        environment: Environment | None = None,
        status: IssueStatus | None = None,
        site_type: SiteType | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[ErrorReport], int]:
        stmt = select(ErrorReport)
        count_stmt = select(func.count()).select_from(ErrorReport)

        if project_code is not None:
            stmt = stmt.where(ErrorReport.project_code == project_code)
            count_stmt = count_stmt.where(ErrorReport.project_code == project_code)
        if environment is not None:
            stmt = stmt.where(ErrorReport.environment == environment)
            count_stmt = count_stmt.where(ErrorReport.environment == environment)
        if status is not None:
            stmt = stmt.where(ErrorReport.report_status == status)
            count_stmt = count_stmt.where(ErrorReport.report_status == status)
        if site_type is not None:
            stmt = stmt.where(ErrorReport.site_type == site_type)
            count_stmt = count_stmt.where(ErrorReport.site_type == site_type)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(ErrorReport.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_group_by_key(self, group_key: str) -> IssueGroup | None:
        stmt = select(IssueGroup).where(IssueGroup.group_key == group_key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_groups(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[IssueGroup], int]:
        stmt = select(IssueGroup)
        count_stmt = select(func.count()).select_from(IssueGroup)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(IssueGroup.last_seen_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def increment_group_count(self, group: IssueGroup) -> IssueGroup:
        group.occurrence_count += 1
        await self.db.flush()
        await self.db.refresh(group)
        return group
