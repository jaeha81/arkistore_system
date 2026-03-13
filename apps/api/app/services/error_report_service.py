"""
에러 리포트 수집 서비스
외부 클라이언트(프론트엔드)에서 에러를 보고할 때 사용
"""
import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import IssueStatus
from app.core.exceptions import IdempotencyConflictException
from app.models.error_report import ErrorReport
from app.models.issue_group import IssueGroup


def _mask_error_message(message: str) -> str:
    """에러 메시지에서 민감 정보 마스킹"""
    # 이메일
    masked = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "***@***.***", message)
    # 전화번호 (한국 형식)
    masked = re.sub(r"\d{2,4}[-.]?\d{3,4}[-.]?\d{4}", "***-****-****", masked)
    # IP 주소
    masked = re.sub(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", "***.***.***.***", masked)
    # JWT 토큰 패턴
    masked = re.sub(r"eyJ[\w-]+\.eyJ[\w-]+\.[\w-]+", "[TOKEN_MASKED]", masked)
    return masked


def _generate_group_key(project_code: str, error_code: str, screen_name: str | None) -> str:
    """이슈 그룹핑용 키 생성"""
    raw = f"{project_code}:{error_code}:{screen_name or 'unknown'}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


async def create_error_report(
    data: dict[str, Any],
    idempotency_key: str | None,
    db: AsyncSession,
) -> dict[str, Any]:
    """
    에러 리포트 생성
    1. Idempotency 체크
    2. 에러 메시지 마스킹
    3. 그룹 키 생성 → IssueGroup find or create
    4. 그룹 카운트 증가
    5. ErrorReport 저장
    6. 응답 반환
    """
    # 1. Idempotency 체크 (trace_id 기반)
    trace_id = data.get("trace_id") or str(uuid.uuid4())
    if idempotency_key:
        existing = await db.execute(
            select(ErrorReport).where(ErrorReport.trace_id == idempotency_key).limit(1)
        )
        if existing.scalar_one_or_none():
            raise IdempotencyConflictException("Duplicate error report")

    # 2. 마스킹
    error_message = data.get("error_message", "")
    error_message_masked = _mask_error_message(error_message)

    # 3. 그룹 키 생성
    project_code = data["project_code"]
    error_code = data["error_code"]
    screen_name = data.get("screen_name")
    group_key = _generate_group_key(project_code, error_code, screen_name)

    # 4. IssueGroup find or create
    now = datetime.now(timezone.utc)
    stmt = select(IssueGroup).where(IssueGroup.group_key == group_key)
    result = await db.execute(stmt)
    group = result.scalar_one_or_none()
    grouped = False

    if group:
        group.occurrence_count += 1
        group.last_seen_at = now
        grouped = True
    else:
        group = IssueGroup(
            group_key=group_key,
            group_title=f"[{project_code}] {error_code} @ {screen_name or 'unknown'}",
            occurrence_count=1,
            first_seen_at=now,
            last_seen_at=now,
            group_status=IssueStatus.new,
        )
        db.add(group)
        await db.flush()

    # 5. ErrorReport 저장
    report = ErrorReport(
        project_code=project_code,
        site_type=data["site_type"],
        environment=data["environment"],
        app_version=data["app_version"],
        screen_name=screen_name,
        error_code=error_code,
        error_message=error_message,
        error_message_masked=error_message_masked,
        user_context=data.get("user_context"),
        report_status=IssueStatus.grouped if grouped else IssueStatus.new,
        issue_group_id=group.id,
        trace_id=idempotency_key or trace_id,
    )
    db.add(report)
    await db.flush()

    # 6. 응답
    return {
        "report_id": str(report.id),
        "trace_id": report.trace_id,
        "grouped": grouped,
    }
