"""
에러 리포트 API 테스트
POST  /api/v1/error-reports
GET   /api/v1/error-reports/groups
PATCH /api/v1/error-reports/groups/{id}/status
"""
import uuid

import pytest
from httpx import AsyncClient


# ==================== 헬퍼 ====================


def _error_report_payload(
    project_code: str = "TEST-PROJECT",
    error_code: str = "ERR_NETWORK",
    screen_name: str = "HomeScreen",
    trace_id: str | None = None,
) -> dict:
    return {
        "project_code": project_code,
        "site_type": "main_dashboard",
        "environment": "production",
        "app_version": "1.0.0",
        "screen_name": screen_name,
        "error_code": error_code,
        "error_message": "Network request failed at https://api.example.com/data",
        "trace_id": trace_id or str(uuid.uuid4()),
        "user_context": {"user_id": "u-123", "session": "s-456"},
    }


# ==================== POST /api/v1/error-reports ====================


async def test_create_error_report_success(client: AsyncClient):
    """에러 리포트 생성 성공 → 201 (인증 불필요)"""
    response = await client.post(
        "/api/v1/error-reports",
        json=_error_report_payload(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "report_id" in data["data"]
    assert "trace_id" in data["data"]
    assert "grouped" in data["data"]
    # 첫 번째 리포트는 그룹핑되지 않음
    assert data["data"]["grouped"] is False


async def test_create_error_report_auto_grouping(client: AsyncClient):
    """동일 project_code + error_code + screen_name → 두 번째는 grouped=True"""
    payload = _error_report_payload(
        project_code="GROUP-TEST",
        error_code="ERR_TIMEOUT",
        screen_name="DashboardScreen",
    )

    # 첫 번째 리포트
    r1 = await client.post("/api/v1/error-reports", json=payload)
    assert r1.status_code == 201
    assert r1.json()["data"]["grouped"] is False

    # 두 번째 리포트 (같은 그룹 키)
    payload2 = {**payload, "trace_id": str(uuid.uuid4())}
    r2 = await client.post("/api/v1/error-reports", json=payload2)
    assert r2.status_code == 201
    assert r2.json()["data"]["grouped"] is True


async def test_create_error_report_with_idempotency_key(client: AsyncClient):
    """Idempotency-Key 헤더 포함 → 201"""
    idem_key = f"error-report-{uuid.uuid4().hex}"
    response = await client.post(
        "/api/v1/error-reports",
        json=_error_report_payload(),
        headers={"Idempotency-Key": idem_key},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["trace_id"] == idem_key


async def test_create_error_report_duplicate_trace_id_409(client: AsyncClient):
    """동일 Idempotency-Key(trace_id) 두 번 → 409"""
    idem_key = f"dup-trace-{uuid.uuid4().hex}"

    r1 = await client.post(
        "/api/v1/error-reports",
        json=_error_report_payload(),
        headers={"Idempotency-Key": idem_key},
    )
    assert r1.status_code == 201

    r2 = await client.post(
        "/api/v1/error-reports",
        json=_error_report_payload(),
        headers={"Idempotency-Key": idem_key},
    )
    assert r2.status_code == 409
    data = r2.json()
    assert data["success"] is False
    assert data["error"]["code"] == "IDEMPOTENCY_CONFLICT"


async def test_create_error_report_different_groups(client: AsyncClient):
    """다른 error_code → 다른 그룹 생성"""
    r1 = await client.post(
        "/api/v1/error-reports",
        json=_error_report_payload(error_code="ERR_A"),
    )
    r2 = await client.post(
        "/api/v1/error-reports",
        json=_error_report_payload(error_code="ERR_B"),
    )
    assert r1.status_code == 201
    assert r2.status_code == 201
    # 둘 다 grouped=False (각각 새 그룹)
    assert r1.json()["data"]["grouped"] is False
    assert r2.json()["data"]["grouped"] is False


# ==================== GET /api/v1/error-reports/groups ====================


async def test_list_issue_groups_empty(client: AsyncClient, auth_headers: dict):
    """그룹 없을 때 빈 목록"""
    response = await client.get("/api/v1/error-reports/groups", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


async def test_list_issue_groups_with_data(client: AsyncClient, auth_headers: dict):
    """에러 리포트 생성 후 그룹 목록 조회"""
    # 에러 리포트 생성 (그룹 자동 생성)
    await client.post(
        "/api/v1/error-reports",
        json=_error_report_payload(project_code="GROUP-LIST-TEST"),
    )

    response = await client.get("/api/v1/error-reports/groups", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["meta"]["total"] >= 1


async def test_list_issue_groups_filter_by_status(client: AsyncClient, auth_headers: dict):
    """status 필터 적용"""
    response = await client.get(
        "/api/v1/error-reports/groups",
        params={"group_status": "new"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    for group in data["data"]:
        assert group["group_status"] == "new"


async def test_list_issue_groups_filter_by_project_code(client: AsyncClient, auth_headers: dict):
    """project_code 필터 적용"""
    unique_code = f"FILTER-{uuid.uuid4().hex[:6].upper()}"
    await client.post(
        "/api/v1/error-reports",
        json=_error_report_payload(project_code=unique_code),
    )

    response = await client.get(
        "/api/v1/error-reports/groups",
        params={"project_code": unique_code},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["meta"]["total"] >= 1
    for group in data["data"]:
        assert unique_code in group["group_title"]


async def test_list_issue_groups_unauthenticated(client: AsyncClient):
    """인증 없이 그룹 목록 조회 → 401"""
    response = await client.get("/api/v1/error-reports/groups")
    assert response.status_code == 401


# ==================== PATCH /api/v1/error-reports/groups/{id}/status ====================


async def test_update_group_status_success(client: AsyncClient, auth_headers: dict):
    """그룹 상태 변경 → 200"""
    # 에러 리포트 생성 → 그룹 생성
    create_resp = await client.post(
        "/api/v1/error-reports",
        json=_error_report_payload(project_code="STATUS-UPDATE-TEST"),
    )
    assert create_resp.status_code == 201

    # 그룹 목록에서 ID 가져오기
    groups_resp = await client.get(
        "/api/v1/error-reports/groups",
        params={"project_code": "STATUS-UPDATE-TEST"},
        headers=auth_headers,
    )
    assert groups_resp.status_code == 200
    groups = groups_resp.json()["data"]
    assert len(groups) >= 1
    group_id = groups[0]["id"]

    # 상태 변경
    update_resp = await client.patch(
        f"/api/v1/error-reports/groups/{group_id}/status",
        json={"group_status": "triaged"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["success"] is True
    assert data["data"]["group_status"] == "triaged"


async def test_update_group_status_not_found(client: AsyncClient, auth_headers: dict):
    """존재하지 않는 그룹 상태 변경 → 404"""
    fake_id = uuid.uuid4()
    response = await client.patch(
        f"/api/v1/error-reports/groups/{fake_id}/status",
        json={"group_status": "resolved"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_update_group_status_unauthenticated(client: AsyncClient):
    """인증 없이 그룹 상태 변경 → 401"""
    fake_id = uuid.uuid4()
    response = await client.patch(
        f"/api/v1/error-reports/groups/{fake_id}/status",
        json={"group_status": "resolved"},
    )
    assert response.status_code == 401


async def test_update_group_status_to_resolved(client: AsyncClient, auth_headers: dict):
    """그룹 상태를 resolved로 변경"""
    unique_code = f"RESOLVE-{uuid.uuid4().hex[:6].upper()}"
    await client.post(
        "/api/v1/error-reports",
        json=_error_report_payload(project_code=unique_code),
    )

    groups_resp = await client.get(
        "/api/v1/error-reports/groups",
        params={"project_code": unique_code},
        headers=auth_headers,
    )
    group_id = groups_resp.json()["data"][0]["id"]

    update_resp = await client.patch(
        f"/api/v1/error-reports/groups/{group_id}/status",
        json={"group_status": "resolved"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["group_status"] == "resolved"
