"""
테스트 픽스처 및 공통 설정
"""
import asyncio
import uuid
from datetime import date, datetime, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.enums import ProjectStatus, SlotStatus
from app.core.security import hash_password
from app.main import app
from app.models.capacity_slot import CapacitySlot
from app.models.project import Project
from app.models.user import User

# 테스트용 SQLite (메모리)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="session")
async def db_setup():
    """테스트 DB 스키마 생성"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(db_setup) -> AsyncGenerator[AsyncSession, None]:
    """각 테스트마다 독립적인 DB 세션 제공"""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """테스트용 HTTP 클라이언트"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ==================== 추가 픽스처 ====================


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """테스트용 사용자 생성"""
    user = User(
        id=uuid.uuid4(),
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        name="테스트 사용자",
        hashed_password=hash_password("testpassword123!"),
        role="ops_admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """로그인 후 Authorization 헤더 반환"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "testpassword123!"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    access_token = data["data"]["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def test_project(db_session: AsyncSession) -> Project:
    """테스트용 프로젝트 생성"""
    project = Project(
        id=uuid.uuid4(),
        project_code=f"TEST-{uuid.uuid4().hex[:6].upper()}",
        name="테스트 프로젝트",
        client_name="테스트 클라이언트",
        service_type="ecommerce",
        main_url="https://test.example.com",
        status=ProjectStatus.active,
    )
    db_session.add(project)
    await db_session.flush()
    return project


@pytest_asyncio.fixture
async def test_capacity_slot(db_session: AsyncSession) -> CapacitySlot:
    """오늘 날짜의 오픈 CAPA 슬롯 생성"""
    slot = CapacitySlot(
        id=uuid.uuid4(),
        slot_date=date.today(),
        delivery_team="팀A",
        time_slot="09:00-12:00",
        max_capacity=10,
        used_capacity=0,
        remaining_capacity=10,
        slot_status=SlotStatus.open,
    )
    db_session.add(slot)
    await db_session.flush()
    return slot
