"""
로그 조회 서비스 (운영 도메인)
"""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.error_report import ErrorReport
from app.models.event_log import EventLog


async def list_event_logs(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[EventLog], int]:
    """이벤트 로그 목록 조회"""
    stmt = select(EventLog)

    if project_code := filters.get("project_code"):
        stmt = stmt.where(EventLog.project_code == project_code)
    if event_type := filters.get("event_type"):
        stmt = stmt.where(EventLog.event_type == event_type)
    if environment := filters.get("environment"):
        stmt = stmt.where(EventLog.environment == environment)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(EventLog.logged_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def list_error_logs(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[ErrorReport], int]:
    """에러 로그 목록 조회"""
    stmt = select(ErrorReport)

    if project_code := filters.get("project_code"):
        stmt = stmt.where(ErrorReport.project_code == project_code)
    if error_code := filters.get("error_code"):
        stmt = stmt.where(ErrorReport.error_code == error_code)
    if status := filters.get("status"):
        stmt = stmt.where(ErrorReport.report_status == status)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(ErrorReport.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total
