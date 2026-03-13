"""
계약 관리 API 테스트 (업무 도메인)
GET   /api/v1/arki/contracts
POST  /api/v1/arki/contracts
PATCH /api/v1/arki/contracts/{id}
"""
import uuid
from datetime import date

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer


# ==================== 로컬 픽스처 ====================


@pytest_asyncio.fixture
async def test_customer(db_session: AsyncSession) -> Customer:
    """테스트용 고객 생성"""
    customer = Customer(
        id=uuid.uuid4(),
        customer_type="individual",
        name="테스트 고객",
        phone="010-1234-5678",
        grade="normal",
    )
    db_session.add(customer)
    await db_session.flush()
    return customer


def _contract_payload(customer_id: uuid.UUID, idempotency_key: str | None = None) -> dict:
    """계약 생성 페이로드 헬퍼"""
    return {
        "customer_id": str(customer_id),
        "contract_date": str(date.today()),
        "contract_amount": 5000000,
        "deposit_amount": 1000000,
        "delivery_required": True,
        "remarks": "테스트 계약",
    }


# ==================== GET /api/v1/arki/contracts ====================


async def test_list_contracts_empty(client: AsyncClient, auth_headers: dict):
    """계약 없을 때 빈 목록 반환"""
    response = await client.get("/api/v1/arki/contracts", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert "total" in data["meta"]


async def test_list_contracts_with_data(
    client: AsyncClient,
    auth_headers: dict,
    test_customer: Customer,
):
    """계약 생성 후 목록 조회"""
    idem_key = f"list-test-{uuid.uuid4().hex}"
    create_resp = await client.post(
        "/api/v1/arki/contracts",
        json=_contract_payload(test_customer.id),
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert create_resp.status_code == 201

    list_resp = await client.get("/api/v1/arki/contracts", headers=auth_headers)
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["meta"]["total"] >= 1


async def test_list_contracts_unauthenticated(client: AsyncClient):
    """인증 없이 목록 조회 → 401"""
    response = await client.get("/api/v1/arki/contracts")
    assert response.status_code == 401


# ==================== POST /api/v1/arki/contracts ====================


async def test_create_contract_success(
    client: AsyncClient,
    auth_headers: dict,
    test_customer: Customer,
):
    """계약 생성 성공 → 201"""
    idem_key = f"contract-create-{uuid.uuid4().hex}"
    response = await client.post(
        "/api/v1/arki/contracts",
        json=_contract_payload(test_customer.id),
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["customer_id"] == str(test_customer.id)
    assert data["data"]["contract_status"] == "draft"
    assert data["data"]["contract_number"] is not None
    assert "id" in data["data"]


async def test_create_contract_missing_idempotency_key(
    client: AsyncClient,
    auth_headers: dict,
    test_customer: Customer,
):
    """Idempotency-Key 헤더 누락 → 422"""
    response = await client.post(
        "/api/v1/arki/contracts",
        json=_contract_payload(test_customer.id),
        headers=auth_headers,  # Idempotency-Key 없음
    )
    assert response.status_code == 422


async def test_create_contract_idempotency_same_key_returns_409(
    client: AsyncClient,
    auth_headers: dict,
    test_customer: Customer,
):
    """동일 Idempotency-Key로 두 번 요청 → 409"""
    idem_key = f"idem-dup-{uuid.uuid4().hex}"
    payload = _contract_payload(test_customer.id)

    # 첫 번째 요청
    r1 = await client.post(
        "/api/v1/arki/contracts",
        json=payload,
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert r1.status_code == 201

    # 두 번째 요청 (동일 키)
    r2 = await client.post(
        "/api/v1/arki/contracts",
        json=payload,
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert r2.status_code == 409
    data = r2.json()
    assert data["success"] is False
    assert data["error"]["code"] == "IDEMPOTENCY_CONFLICT"


async def test_create_contract_different_keys_succeed(
    client: AsyncClient,
    auth_headers: dict,
    test_customer: Customer,
):
    """서로 다른 Idempotency-Key → 각각 성공"""
    payload = _contract_payload(test_customer.id)

    r1 = await client.post(
        "/api/v1/arki/contracts",
        json=payload,
        headers={**auth_headers, "Idempotency-Key": f"key-a-{uuid.uuid4().hex}"},
    )
    r2 = await client.post(
        "/api/v1/arki/contracts",
        json=payload,
        headers={**auth_headers, "Idempotency-Key": f"key-b-{uuid.uuid4().hex}"},
    )
    assert r1.status_code == 201
    assert r2.status_code == 201
    # 서로 다른 계약번호
    assert r1.json()["data"]["contract_number"] != r2.json()["data"]["contract_number"]


# ==================== PATCH /api/v1/arki/contracts/{id} ====================


async def test_update_contract_status_valid_transition(
    client: AsyncClient,
    auth_headers: dict,
    test_customer: Customer,
):
    """draft → signed 상태 전이 → 200"""
    idem_key = f"update-status-{uuid.uuid4().hex}"
    create_resp = await client.post(
        "/api/v1/arki/contracts",
        json=_contract_payload(test_customer.id),
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert create_resp.status_code == 201
    contract_id = create_resp.json()["data"]["id"]

    update_resp = await client.patch(
        f"/api/v1/arki/contracts/{contract_id}",
        json={"contract_status": "signed"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["success"] is True
    assert data["data"]["contract_status"] == "signed"


async def test_update_contract_status_invalid_transition(
    client: AsyncClient,
    auth_headers: dict,
    test_customer: Customer,
):
    """draft → confirmed (허용되지 않는 전이) → 422"""
    idem_key = f"invalid-transition-{uuid.uuid4().hex}"
    create_resp = await client.post(
        "/api/v1/arki/contracts",
        json=_contract_payload(test_customer.id),
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert create_resp.status_code == 201
    contract_id = create_resp.json()["data"]["id"]

    # draft에서 confirmed로 직접 전이는 불가 (draft → signed → confirmed)
    update_resp = await client.patch(
        f"/api/v1/arki/contracts/{contract_id}",
        json={"contract_status": "confirmed"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 422
    data = update_resp.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_STATUS_TRANSITION"


async def test_update_contract_not_found(client: AsyncClient, auth_headers: dict):
    """존재하지 않는 계약 수정 → 404"""
    fake_id = uuid.uuid4()
    response = await client.patch(
        f"/api/v1/arki/contracts/{fake_id}",
        json={"contract_status": "signed"},
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "CONTRACT_NOT_FOUND"


async def test_update_contract_remarks(
    client: AsyncClient,
    auth_headers: dict,
    test_customer: Customer,
):
    """계약 비고 수정 → 200"""
    idem_key = f"update-remarks-{uuid.uuid4().hex}"
    create_resp = await client.post(
        "/api/v1/arki/contracts",
        json=_contract_payload(test_customer.id),
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert create_resp.status_code == 201
    contract_id = create_resp.json()["data"]["id"]

    update_resp = await client.patch(
        f"/api/v1/arki/contracts/{contract_id}",
        json={"remarks": "수정된 비고 내용"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["data"]["remarks"] == "수정된 비고 내용"
