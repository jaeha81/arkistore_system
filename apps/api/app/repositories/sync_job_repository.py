"""
Google Sheets 동기화 작업 리포지토리
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import SyncJobStatus
from app.models.sheet_sync_job import SheetSyncJob
from app.repositories.base import BaseRepository


class SyncJobRepository(BaseRepository[SheetSyncJob]):
    model = SheetSyncJob

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_idempotency_key(self, key: str) -> SheetSyncJob | None:
        stmt = select(SheetSyncJob).where(SheetSyncJob.idempotency_key == key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_with_filters(
        self,
        project_code: str | None = None,
        job_status: SyncJobStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[SheetSyncJob], int]:
        stmt = select(SheetSyncJob)
        count_stmt = select(func.count()).select_from(SheetSyncJob)

        if project_code is not None:
            stmt = stmt.where(SheetSyncJob.project_code == project_code)
            count_stmt = count_stmt.where(SheetSyncJob.project_code == project_code)
        if job_status is not None:
            stmt = stmt.where(SheetSyncJob.job_status == job_status)
            count_stmt = count_stmt.where(SheetSyncJob.job_status == job_status)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(SheetSyncJob.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total
