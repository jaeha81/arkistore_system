"""
에러 리포트 서비스 유닛 테스트
직접 서비스 함수를 호출하여 비즈니스 로직 검증
"""
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import IdempotencyConflictException
from app.services.error_report_service import (
    _generate_group_key,
    _mask_error_message,
    create_error_report,
)


# ==================== _mask_error_message ====================


def test_mask_email():
    """이메일 주소 마스킹"""
    msg = "User john.doe@example.com failed to authenticate"
    masked = _mask_error_message(msg)
    assert "john.doe@example.com" not in masked
    assert "***@***.***" in masked


def test_mask_phone_korean_format():
    """한국 전화번호 마스킹"""
    msg = "고객 전화번호: 010-1234-5678 로 연락 바랍니다"
    masked = _mask_error_message(msg)
    assert "010-1234-5678" not in masked
    assert "***-****-****" in masked


def test_mask_phone_without_dashes():
    """대시 없는 전화번호 마스킹"""
    msg = "Phone: 01012345678"
    masked = _mask_error_message(msg)
    assert "01012345678" not in masked


def test_mask_ip_address():
    """IP 주소 마스킹"""
    msg = "Connection from 192.168.1.100 was rejected"
    masked = _mask_error_message(msg)
    assert "192.168.1.100" not in masked
    assert "***.***.***.***" in masked


def test_mask_jwt_token():
    """JWT 토큰 마스킹"""
    # 실제 JWT 형식: eyJ...eyJ...signature
    jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    msg = f"Invalid token: {jwt}"
    masked = _mask_error_message(msg)
    assert jwt not in masked
    assert "[TOKEN_MASKED]" in masked


def test_mask_multiple_sensitive_data():
    """여러 민감 정보 동시 마스킹"""
    msg = (
        "User test@example.com from IP 10.0.0.1 "
        "with phone 010-9876-5432 sent invalid token"
    )
    masked = _mask_error_message(msg)
    assert "test@example.com" not in masked
    assert "10.0.0.1" not in masked
    assert "010-9876-5432" not in masked


def test_mask_no_sensitive_data():
    """민감 정보 없는 메시지 → 변경 없음"""
    msg = "Network timeout occurred while fetching data"
    masked = _mask_error_message(msg)
    assert masked == msg


def test_mask_empty_string():
    """빈 문자열 → 빈 문자열"""
    assert _mask_error_message("") == ""


# ==================== _generate_group_key ====================


def test_generate_group_key_deterministic():
    """동일 입력 → 동일 키"""
    key1 = _generate_group_key("PROJECT-A", "ERR_NETWORK", "HomeScreen")
    key2 = _generate_group_key("PROJECT-A", "ERR_NETWORK", "HomeScreen")
    assert key1 == key2


def test_generate_group_key_different_project():
    """다른 project_code → 다른 키"""
    key1 = _generate_group_key("PROJECT-A", "ERR_NETWORK", "HomeScreen")
    key2 = _generate_group_key("PROJECT-B", "ERR_NETWORK", "HomeScreen")
    assert key1 != key2


def test_generate_group_key_different_error_code():
    """다른 error_code → 다른 키"""
    key1 = _generate_group_key("PROJECT-A", "ERR_NETWORK", "HomeScreen")
    key2 = _generate_group_key("PROJECT-A", "ERR_TIMEOUT", "HomeScreen")
    assert key1 != key2


def test_generate_group_key_none_screen_name():
    """screen_name=None → 'unknown' 사용"""
    key1 = _generate_group_key("PROJECT-A", "ERR_NETWORK", None)
    key2 = _generate_group_key("PROJECT-A", "ERR_NETWORK", "unknown")
    assert key1 == key2


def test_generate_group_key_length():
    """키 길이는 32자"""
    key = _generate_group_key("PROJECT-A", "ERR_NETWORK", "HomeScreen")
    assert len(key) == 32


# ==================== create_error_report ====================


def _report_data(
    project_code: str = "TEST-SVC",
    error_code: str = "ERR_TEST",
    screen_name: str = "TestScreen",
) -> dict:
    return {
        "project_code": project_code,
        "site_type": "main_dashboard",
        "environment": "production",
        "app_version": "1.0.0",
        "screen_name": screen_name,
        "error_code": error_code,
        "error_message": "Test error occurred",
        "trace_id": str(uuid.uuid4()),
    }


async def test_create_error_report_first_report_creates_new_group(
    db_session: AsyncSession,
):
    """첫 번째 리포트 → 새 그룹 생성, grouped=False"""
    data = _report_data(project_code=f"FIRST-{uuid.uuid4().hex[:6]}")
    result = await create_error_report(data=data, idempotency_key=None, db=db_session)

    assert "report_id" in result
    assert "trace_id" in result
    assert result["grouped"] is False


async def test_create_error_report_second_same_key_increments_occurrence_count(
    db_session: AsyncSession,
):
    """두 번째 동일 그룹 키 리포트 → occurrence_count 증가, grouped=True"""
    from sqlalchemy import select

    from app.models.issue_group import IssueGroup
    from app.services.error_report_service import _generate_group_key

    project_code = f"SECOND-{uuid.uuid4().hex[:6]}"
    error_code = "ERR_REPEAT"
    screen_name = "RepeatScreen"

    data1 = _report_data(project_code=project_code, error_code=error_code, screen_name=screen_name)
    data2 = {**data1, "trace_id": str(uuid.uuid4())}

    # 첫 번째 리포트
    r1 = await create_error_report(data=data1, idempotency_key=None, db=db_session)
    assert r1["grouped"] is False

    # 두 번째 리포트 (동일 그룹 키)
    r2 = await create_error_report(data=data2, idempotency_key=None, db=db_session)
    assert r2["grouped"] is True

    # 그룹 occurrence_count 확인
    group_key = _generate_group_key(project_code, error_code, screen_name)
    stmt = select(IssueGroup).where(IssueGroup.group_key == group_key)
    result = await db_session.execute(stmt)
    group = result.scalar_one_or_none()

    assert group is not None
    assert group.occurrence_count == 2


async def test_create_error_report_third_report_increments_to_three(
    db_session: AsyncSession,
):
    """세 번째 리포트 → occurrence_count == 3"""
    from sqlalchemy import select

    from app.models.issue_group import IssueGroup
    from app.services.error_report_service import _generate_group_key

    project_code = f"THIRD-{uuid.uuid4().hex[:6]}"
    error_code = "ERR_TRIPLE"
    screen_name = "TripleScreen"

    for i in range(3):
        data = _report_data(project_code=project_code, error_code=error_code, screen_name=screen_name)
        data["trace_id"] = str(uuid.uuid4())
        await create_error_report(data=data, idempotency_key=None, db=db_session)

    group_key = _generate_group_key(project_code, error_code, screen_name)
    stmt = select(IssueGroup).where(IssueGroup.group_key == group_key)
    result = await db_session.execute(stmt)
    group = result.scalar_one_or_none()

    assert group is not None
    assert group.occurrence_count == 3


async def test_create_error_report_idempotency_conflict(
    db_session: AsyncSession,
):
    """동일 idempotency_key 두 번 → IdempotencyConflictException"""
    idem_key = f"idem-err-{uuid.uuid4().hex}"
    data = _report_data()

    # 첫 번째
    await create_error_report(data=data, idempotency_key=idem_key, db=db_session)

    # 두 번째 (동일 키)
    with pytest.raises(IdempotencyConflictException) as exc_info:
        await create_error_report(data=data, idempotency_key=idem_key, db=db_session)

    assert exc_info.value.code == "IDEMPOTENCY_CONFLICT"


async def test_create_error_report_masks_sensitive_data(
    db_session: AsyncSession,
):
    """에러 메시지의 민감 정보가 마스킹되어 저장됨"""
    from sqlalchemy import select

    from app.models.error_report import ErrorReport

    sensitive_msg = "User admin@company.com from 192.168.0.1 failed"
    data = _report_data()
    data["error_message"] = sensitive_msg

    result = await create_error_report(data=data, idempotency_key=None, db=db_session)

    # DB에서 리포트 조회
    stmt = select(ErrorReport).where(ErrorReport.id == uuid.UUID(result["report_id"]))
    db_result = await db_session.execute(stmt)
    report = db_result.scalar_one_or_none()

    assert report is not None
    # 원본 메시지는 보존
    assert report.error_message == sensitive_msg
    # 마스킹된 메시지에는 민감 정보 없음
    assert "admin@company.com" not in report.error_message_masked
    assert "192.168.0.1" not in report.error_message_masked


async def test_create_error_report_without_idempotency_key(
    db_session: AsyncSession,
):
    """idempotency_key=None → trace_id는 data의 trace_id 사용"""
    trace_id = str(uuid.uuid4())
    data = _report_data()
    data["trace_id"] = trace_id

    result = await create_error_report(data=data, idempotency_key=None, db=db_session)

    assert result["trace_id"] == trace_id


async def test_create_error_report_with_idempotency_key_overrides_trace_id(
    db_session: AsyncSession,
):
    """idempotency_key 제공 시 trace_id로 사용됨"""
    idem_key = f"override-{uuid.uuid4().hex}"
    data = _report_data()
    data["trace_id"] = str(uuid.uuid4())  # 다른 trace_id

    result = await create_error_report(data=data, idempotency_key=idem_key, db=db_session)

    # idempotency_key가 trace_id로 저장됨
    assert result["trace_id"] == idem_key


async def test_create_error_report_different_groups_independent(
    db_session: AsyncSession,
):
    """다른 그룹 키 → 각각 독립적인 그룹"""
    from sqlalchemy import select

    from app.models.issue_group import IssueGroup

    project_code = f"INDEP-{uuid.uuid4().hex[:6]}"

    data_a = _report_data(project_code=project_code, error_code="ERR_A")
    data_b = _report_data(project_code=project_code, error_code="ERR_B")

    await create_error_report(data=data_a, idempotency_key=None, db=db_session)
    await create_error_report(data=data_b, idempotency_key=None, db=db_session)

    # 두 그룹이 각각 생성됨
    stmt = select(IssueGroup).where(IssueGroup.group_title.contains(project_code))
    result = await db_session.execute(stmt)
    groups = list(result.scalars().all())

    assert len(groups) == 2
    for group in groups:
        assert group.occurrence_count == 1
