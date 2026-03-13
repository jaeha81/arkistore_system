"""
시트 동기화 서비스
Google Sheets 내보내기 작업 관리
"""
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import SyncJobStatus
from app.core.exceptions import IdempotencyConflictException, NotFoundException
from app.models.sheet_sync_job import SheetSyncJob


async def create_export_job(
    data: dict[str, Any],
    idempotency_key: str | None,
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> SheetSyncJob:
    """내보내기 작업 생성 (멱등성 체크, 비동기 실행은 placeholder)"""
    if idempotency_key:
        existing = await db.execute(
            select(SheetSyncJob)
            .where(SheetSyncJob.idempotency_key == idempotency_key)
            .limit(1)
        )
        if existing.scalar_one_or_none():
            raise IdempotencyConflictException("Duplicate export job request")

    job = SheetSyncJob(
        **data,
        job_status=SyncJobStatus.pending.value,
        created_by=actor_user_id,
        idempotency_key=idempotency_key,
    )
    db.add(job)
    await db.flush()

    # TODO: Phase 2 - Celery/ARQ 태스크로 실제 내보내기 실행
    # async_export_task.delay(str(job.id))

    return job


async def get_job_status(
    job_id: uuid.UUID,
    db: AsyncSession,
) -> SheetSyncJob:
    """작업 상태 조회"""
    stmt = select(SheetSyncJob).where(SheetSyncJob.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("Sync job not found")
    return job
