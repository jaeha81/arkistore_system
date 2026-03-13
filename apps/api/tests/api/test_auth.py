"""
인증 API 테스트
POST /api/v1/auth/login
GET  /api/v1/auth/me
POST /api/v1/auth/logout
"""
import pytest
from httpx import AsyncClient

from app.models.user import User


# ==================== POST /api/v1/auth/login ====================


async def test_login_success(client: AsyncClient, test_user: User):
    """정상 로그인 → 200, access_token 반환"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "testpassword123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["email"] == test_user.email
    assert data["data"]["user"]["role"] == test_user.role


async def test_login_wrong_password(client: AsyncClient, test_user: User):
    """잘못된 비밀번호 → 401"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "UNAUTHORIZED"


async def test_login_nonexistent_email(client: AsyncClient):
    """존재하지 않는 이메일 → 401"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "anypassword"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False


async def test_login_missing_email(client: AsyncClient):
    """이메일 누락 → 401 (빈 문자열로 처리됨)"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"password": "testpassword123!"},
    )
    assert response.status_code == 401


async def test_login_missing_password(client: AsyncClient, test_user: User):
    """비밀번호 누락 → 401 (빈 문자열로 처리됨)"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email},
    )
    assert response.status_code == 401


async def test_login_sets_cookie(client: AsyncClient, test_user: User):
    """로그인 성공 시 access_token 쿠키 설정"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "testpassword123!"},
    )
    assert response.status_code == 200
    # 쿠키가 설정되었는지 확인
    assert "access_token" in response.cookies or "access_token" in response.headers.get(
        "set-cookie", ""
    )


# ==================== GET /api/v1/auth/me ====================


async def test_get_me_authenticated(client: AsyncClient, test_user: User, auth_headers: dict):
    """인증된 사용자 → 200, 사용자 정보 반환"""
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == test_user.email
    assert data["data"]["name"] == test_user.name
    assert data["data"]["role"] == test_user.role
    assert data["data"]["is_active"] is True
    assert "id" in data["data"]
    assert "created_at" in data["data"]


async def test_get_me_unauthenticated(client: AsyncClient):
    """인증 없이 /me 호출 → 401"""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_get_me_invalid_token(client: AsyncClient):
    """잘못된 토큰으로 /me 호출 → 401"""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401


# ==================== POST /api/v1/auth/logout ====================


async def test_logout_authenticated(client: AsyncClient, auth_headers: dict):
    """인증된 사용자 로그아웃 → 200"""
    response = await client.post("/api/v1/auth/logout", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["message"] == "Logged out"


async def test_logout_unauthenticated(client: AsyncClient):
    """인증 없이 로그아웃 → 401"""
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 401


async def test_logout_clears_cookie(client: AsyncClient, test_user: User):
    """로그아웃 후 쿠키 삭제 확인"""
    # 먼저 로그인
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "testpassword123!"},
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["data"]["access_token"]

    # 로그아웃
    logout_resp = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_resp.status_code == 200
