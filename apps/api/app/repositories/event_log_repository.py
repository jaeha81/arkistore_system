"""
이벤트 로그 리포지토리
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import Environment
from app.models.event_log import EventLog
from app.repositories.base import BaseRepository


class EventLogRepository(BaseRepository[EventLog]):
    model = EventLog

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def list_with_filters(
        self,
        project_code: str | None = None,
        environment: Environment | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[EventLog], int]:
        stmt = select(EventLog)
        count_stmt = select(func.count()).select_from(EventLog)

        if project_code is not None:
            stmt = stmt.where(EventLog.project_code == project_code)
            count_stmt = count_stmt.where(EventLog.project_code == project_code)
        if environment is not None:
            stmt = stmt.where(EventLog.environment == environment)
            count_stmt = count_stmt.where(EventLog.environment == environment)

        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(EventLog.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def bulk_create(self, logs: list[EventLog]) -> None:
        self.db.add_all(logs)
        await self.db.flush()
