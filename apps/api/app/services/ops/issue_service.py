"""
이슈(에러 리포트) 관리 서비스 (운영 도메인)
"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import IssueStatus
from app.core.exceptions import (
    GithubIntegrationException,
    InvalidStatusTransitionException,
    IssueNotFoundException,
    NotFoundException,
)
from app.models.error_report import ErrorReport
from app.models.github_issue import GithubIssue
from app.models.issue_group import IssueGroup
from app.services.audit_service import log_action


# ==================== Mock Adapter ====================

class MockGithubAdapter:
    """GitHub API placeholder (Phase 2에서 실제 연동)"""

    @staticmethod
    async def create_issue(
        repository: str,
        title: str,
        body: str,
        labels: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            "number": 1,
            "html_url": f"https://github.com/{repository}/issues/1",
            "state": "open",
        }


_github = MockGithubAdapter()


async def list_issues(
    filters: dict[str, Any],
    db: AsyncSession,
) -> tuple[list[ErrorReport], int]:
    """에러 리포트 목록 조회"""
    stmt = select(ErrorReport)

    if project_code := filters.get("project_code"):
        stmt = stmt.where(ErrorReport.project_code == project_code)
    if status := filters.get("status"):
        stmt = stmt.where(ErrorReport.report_status == status)
    if error_code := filters.get("error_code"):
        stmt = stmt.where(ErrorReport.error_code == error_code)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    page = filters.get("page", 1)
    page_size = filters.get("page_size", 20)
    stmt = stmt.order_by(ErrorReport.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def get_issue(
    issue_id: uuid.UUID,
    db: AsyncSession,
) -> ErrorReport:
    """에러 리포트 단건 조회"""
    stmt = select(ErrorReport).where(ErrorReport.id == issue_id)
    result = await db.execute(stmt)
    issue = result.scalar_one_or_none()
    if not issue:
        raise IssueNotFoundException()
    return issue


async def update_issue_status(
    issue_id: uuid.UUID,
    status: IssueStatus,
    reason: str | None,
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> ErrorReport:
    """에러 리포트 상태 변경 + 감사 로그"""
    issue = await get_issue(issue_id, db)

    before_status = issue.report_status.value if issue.report_status else None
    issue.report_status = status
    await db.flush()

    await log_action(
        db,
        actor_user_id=actor_user_id,
        action_type="issue.status_change",
        target_table="error_reports",
        target_id=str(issue_id),
        before_data={"status": before_status},
        after_data={"status": status.value, "reason": reason},
    )
    return issue


async def list_issue_groups(
    skip: int,
    limit: int,
    db: AsyncSession,
) -> tuple[list[IssueGroup], int]:
    """이슈 그룹 목록 조회"""
    stmt = select(IssueGroup).order_by(IssueGroup.last_seen_at.desc())

    count_stmt = select(func.count()).select_from(IssueGroup)
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_github_issue(
    group_id: uuid.UUID,
    repository: str,
    labels: list[str] | None,
    db: AsyncSession,
    actor_user_id: uuid.UUID,
) -> dict[str, Any]:
    """이슈 그룹 → GitHub Issue 생성 + 감사 로그"""
    # 그룹 조회
    stmt = select(IssueGroup).where(IssueGroup.id == group_id)
    result = await db.execute(stmt)
    group = result.scalar_one_or_none()
    if not group:
        raise NotFoundException("Issue group not found")

    # GitHub 이슈 생성 (Mock)
    gh_result = await _github.create_issue(
        repository=repository,
        title=group.group_title,
        body=f"Auto-created from issue group {group.group_key}\nOccurrences: {group.occurrence_count}",
        labels=labels,
    )

    # DB 기록
    gh_issue = GithubIssue(
        issue_group_id=group_id,
        repository=repository,
        github_issue_number=gh_result["number"],
        github_issue_url=gh_result["html_url"],
        state=gh_result["state"],
        created_by=actor_user_id,
    )
    db.add(gh_issue)

    # 그룹 상태 업데이트
    group.group_status = IssueStatus.github_created
    group.github_issue_id = gh_issue.id
    await db.flush()

    await log_action(
        db,
        actor_user_id=actor_user_id,
        action_type="issue_group.github_create",
        target_table="issue_groups",
        target_id=str(group_id),
        after_data={
            "repository": repository,
            "github_issue_number": gh_result["number"],
            "github_issue_url": gh_result["html_url"],
        },
    )

    return {
        "github_issue_id": str(gh_issue.id),
        "github_issue_number": gh_result["number"],
        "github_issue_url": gh_result["html_url"],
        "group_id": str(group_id),
    }
