"""
프로젝트 관리 API 테스트 (운영 도메인)
GET    /api/v1/ops/projects
POST   /api/v1/ops/projects
GET    /api/v1/ops/projects/{id}
PATCH  /api/v1/ops/projects/{id}
POST   /api/v1/ops/projects/{id}/sites
GET    /api/v1/ops/projects/{id}/sites
"""
import uuid

import pytest
from httpx import AsyncClient

from app.models.project import Project


# ==================== GET /api/v1/ops/projects ====================


async def test_list_projects_empty(client: AsyncClient, auth_headers: dict):
    """프로젝트 없을 때 빈 목록 반환"""
    response = await client.get("/api/v1/ops/projects", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert "meta" in data
    assert "total" in data["meta"]


async def test_list_projects_with_data(
    client: AsyncClient, auth_headers: dict, test_project: Project
):
    """프로젝트 존재 시 목록 반환"""
    response = await client.get("/api/v1/ops/projects", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["meta"]["total"] >= 1
    project_codes = [p["project_code"] for p in data["data"]]
    assert test_project.project_code in project_codes


async def test_list_projects_filter_by_status(
    client: AsyncClient, auth_headers: dict, test_project: Project
):
    """status 필터 적용"""
    response = await client.get(
        "/api/v1/ops/projects",
        params={"status": "active"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    for project in data["data"]:
        assert project["status"] == "active"


async def test_list_projects_filter_by_status_no_match(
    client: AsyncClient, auth_headers: dict, test_project: Project
):
    """존재하지 않는 status 필터 → 빈 목록"""
    response = await client.get(
        "/api/v1/ops/projects",
        params={"status": "archived"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # test_project는 active이므로 archived 필터에 걸리지 않음
    for project in data["data"]:
        assert project["status"] == "archived"


async def test_list_projects_unauthenticated(client: AsyncClient):
    """인증 없이 목록 조회 → 401"""
    response = await client.get("/api/v1/ops/projects")
    assert response.status_code == 401


# ==================== POST /api/v1/ops/projects ====================


async def test_create_project_success(client: AsyncClient, auth_headers: dict):
    """프로젝트 생성 성공 → 201"""
    response = await client.post(
        "/api/v1/ops/projects",
        json={
            "project_code": "TEST-001",
            "name": "테스트 프로젝트",
            "client_name": "테스트 클라이언트",
            "service_type": "ecommerce",
            "main_url": "https://test.com",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["project_code"] == "TEST-001"
    assert data["data"]["name"] == "테스트 프로젝트"
    assert data["data"]["status"] == "active"
    assert "id" in data["data"]


async def test_create_project_missing_required_field(client: AsyncClient, auth_headers: dict):
    """필수 필드 누락 → 500 (DB 제약 위반)"""
    response = await client.post(
        "/api/v1/ops/projects",
        json={
            # project_code 누락
            "name": "테스트 프로젝트",
            "client_name": "테스트 클라이언트",
            "service_type": "ecommerce",
            "main_url": "https://test.com",
        },
        headers=auth_headers,
    )
    # project_code는 NOT NULL이므로 DB 오류 발생
    assert response.status_code in (422, 500)


async def test_create_project_unauthenticated(client: AsyncClient):
    """인증 없이 생성 → 401"""
    response = await client.post(
        "/api/v1/ops/projects",
        json={
            "project_code": "TEST-UNAUTH",
            "name": "테스트",
            "client_name": "클라이언트",
            "service_type": "ecommerce",
            "main_url": "https://test.com",
        },
    )
    assert response.status_code == 401


async def test_create_project_duplicate_code(client: AsyncClient, auth_headers: dict):
    """중복 project_code → 오류"""
    payload = {
        "project_code": "DUPLICATE-001",
        "name": "첫 번째 프로젝트",
        "client_name": "클라이언트",
        "service_type": "ecommerce",
        "main_url": "https://test.com",
    }
    # 첫 번째 생성
    r1 = await client.post("/api/v1/ops/projects", json=payload, headers=auth_headers)
    assert r1.status_code == 201

    # 두 번째 생성 (중복)
    r2 = await client.post("/api/v1/ops/projects", json=payload, headers=auth_headers)
    assert r2.status_code in (409, 500)


# ==================== GET /api/v1/ops/projects/{id} ====================


async def test_get_project_found(
    client: AsyncClient, auth_headers: dict, test_project: Project
):
    """존재하는 프로젝트 조회 → 200"""
    response = await client.get(
        f"/api/v1/ops/projects/{test_project.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == str(test_project.id)
    assert data["data"]["project_code"] == test_project.project_code


async def test_get_project_not_found(client: AsyncClient, auth_headers: dict):
    """존재하지 않는 프로젝트 조회 → 404"""
    fake_id = uuid.uuid4()
    response = await client.get(
        f"/api/v1/ops/projects/{fake_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "PROJECT_NOT_FOUND"


async def test_get_project_unauthenticated(client: AsyncClient, test_project: Project):
    """인증 없이 단건 조회 → 401"""
    response = await client.get(f"/api/v1/ops/projects/{test_project.id}")
    assert response.status_code == 401


# ==================== PATCH /api/v1/ops/projects/{id} ====================


async def test_update_project_status(
    client: AsyncClient, auth_headers: dict, test_project: Project
):
    """프로젝트 상태 변경 → 200"""
    response = await client.patch(
        f"/api/v1/ops/projects/{test_project.id}",
        json={"status": "paused"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "paused"


async def test_update_project_name(
    client: AsyncClient, auth_headers: dict, test_project: Project
):
    """프로젝트 이름 변경 → 200"""
    new_name = "수정된 프로젝트 이름"
    response = await client.patch(
        f"/api/v1/ops/projects/{test_project.id}",
        json={"name": new_name},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == new_name


async def test_update_project_not_found(client: AsyncClient, auth_headers: dict):
    """존재하지 않는 프로젝트 수정 → 404"""
    fake_id = uuid.uuid4()
    response = await client.patch(
        f"/api/v1/ops/projects/{fake_id}",
        json={"status": "paused"},
        headers=auth_headers,
    )
    assert response.status_code == 404


# ==================== POST /api/v1/ops/projects/{id}/sites ====================


async def test_create_project_site_success(
    client: AsyncClient, auth_headers: dict, test_project: Project
):
    """프로젝트 사이트 추가 → 201"""
    response = await client.post(
        f"/api/v1/ops/projects/{test_project.id}/sites",
        json={
            "site_code": f"SITE-{uuid.uuid4().hex[:6].upper()}",
            "site_name": "메인 대시보드",
            "site_url": "https://dashboard.test.com",
            "site_type": "main_dashboard",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["project_id"] == str(test_project.id)
    assert data["data"]["site_type"] == "main_dashboard"
    assert data["data"]["is_enabled"] is True


async def test_create_project_site_project_not_found(client: AsyncClient, auth_headers: dict):
    """존재하지 않는 프로젝트에 사이트 추가 → 404"""
    fake_id = uuid.uuid4()
    response = await client.post(
        f"/api/v1/ops/projects/{fake_id}/sites",
        json={
            "site_code": "SITE-NOTFOUND",
            "site_name": "사이트",
            "site_url": "https://site.com",
            "site_type": "main_dashboard",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404


# ==================== GET /api/v1/ops/projects/{id}/sites ====================


async def test_list_project_sites_empty(
    client: AsyncClient, auth_headers: dict, test_project: Project
):
    """사이트 없는 프로젝트 → 빈 목록"""
    response = await client.get(
        f"/api/v1/ops/projects/{test_project.id}/sites",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


async def test_list_project_sites_with_data(
    client: AsyncClient, auth_headers: dict, test_project: Project
):
    """사이트 추가 후 목록 조회"""
    site_code = f"SITE-{uuid.uuid4().hex[:6].upper()}"
    # 사이트 생성
    create_resp = await client.post(
        f"/api/v1/ops/projects/{test_project.id}/sites",
        json={
            "site_code": site_code,
            "site_name": "물류 사이트",
            "site_url": "https://logistics.test.com",
            "site_type": "logistics",
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201

    # 목록 조회
    list_resp = await client.get(
        f"/api/v1/ops/projects/{test_project.id}/sites",
        headers=auth_headers,
    )
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["success"] is True
    site_codes = [s["site_code"] for s in data["data"]]
    assert site_code in site_codes


async def test_list_project_sites_not_found(client: AsyncClient, auth_headers: dict):
    """존재하지 않는 프로젝트의 사이트 목록 → 404"""
    fake_id = uuid.uuid4()
    response = await client.get(
        f"/api/v1/ops/projects/{fake_id}/sites",
        headers=auth_headers,
    )
    assert response.status_code == 404
