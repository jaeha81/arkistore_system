"""
배달(납품) API 테스트 (업무 도메인)
GET   /api/v1/arki/deliveries
POST  /api/v1/arki/deliveries
PATCH /api/v1/arki/deliveries/{id}
"""
import uuid
from datetime import date

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import DeliveryStatus, SlotStatus
from app.models.capacity_slot import CapacitySlot
from app.models.contract import Contract
from app.models.customer import Customer
from app.models.delivery import Delivery


# ==================== 로컬 픽스처 ====================


@pytest_asyncio.fixture
async def test_customer(db_session: AsyncSession) -> Customer:
    customer = Customer(
        id=uuid.uuid4(),
        customer_type="individual",
        name="배달 테스트 고객",
        grade="normal",
    )
    db_session.add(customer)
    await db_session.flush()
    return customer


@pytest_asyncio.fixture
async def test_contract(db_session: AsyncSession, test_customer: Customer) -> Contract:
    contract = Contract(
        id=uuid.uuid4(),
        customer_id=test_customer.id,
        contract_date=date.today(),
        contract_amount=5000000,
        contract_status="draft",
        delivery_required=True,
        created_by=None,
        idempotency_key=f"contract-{uuid.uuid4().hex}",
    )
    db_session.add(contract)
    await db_session.flush()
    return contract


@pytest_asyncio.fixture
async def test_slot(db_session: AsyncSession) -> CapacitySlot:
    """오늘 날짜의 오픈 슬롯"""
    slot = CapacitySlot(
        id=uuid.uuid4(),
        slot_date=date.today(),
        delivery_team="배달팀A",
        time_slot="09:00-12:00",
        max_capacity=10,
        used_capacity=0,
        remaining_capacity=10,
        slot_status=SlotStatus.open,
    )
    db_session.add(slot)
    await db_session.flush()
    return slot


@pytest_asyncio.fixture
async def test_full_slot(db_session: AsyncSession) -> CapacitySlot:
    """꽉 찬 슬롯"""
    slot = CapacitySlot(
        id=uuid.uuid4(),
        slot_date=date.today(),
        delivery_team="배달팀B",
        time_slot="13:00-17:00",
        max_capacity=2,
        used_capacity=2,
        remaining_capacity=0,
        slot_status=SlotStatus.full,
    )
    db_session.add(slot)
    await db_session.flush()
    return slot


def _delivery_payload(
    contract_id: uuid.UUID,
    customer_id: uuid.UUID,
    delivery_team: str = "배달팀A",
    time_slot: str = "09:00-12:00",
) -> dict:
    return {
        "contract_id": str(contract_id),
        "customer_id": str(customer_id),
        "delivery_date": str(date.today()),
        "time_slot": time_slot,
        "delivery_team": delivery_team,
        "address_text": "서울시 강남구 테스트로 123",
        "ladder_required": False,
    }


# ==================== GET /api/v1/arki/deliveries ====================


async def test_list_deliveries_empty(client: AsyncClient, auth_headers: dict):
    """배달 없을 때 빈 목록"""
    response = await client.get("/api/v1/arki/deliveries", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert "total" in data["meta"]


async def test_list_deliveries_with_data(
    client: AsyncClient,
    auth_headers: dict,
    test_contract: Contract,
    test_customer: Customer,
    test_slot: CapacitySlot,
):
    """배달 생성 후 목록 조회"""
    idem_key = f"delivery-list-{uuid.uuid4().hex}"
    create_resp = await client.post(
        "/api/v1/arki/deliveries",
        json=_delivery_payload(test_contract.id, test_customer.id),
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert create_resp.status_code == 201

    list_resp = await client.get("/api/v1/arki/deliveries", headers=auth_headers)
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["meta"]["total"] >= 1


async def test_list_deliveries_filter_by_date(
    client: AsyncClient,
    auth_headers: dict,
    test_contract: Contract,
    test_customer: Customer,
    test_slot: CapacitySlot,
):
    """날짜 필터 적용"""
    idem_key = f"delivery-date-filter-{uuid.uuid4().hex}"
    await client.post(
        "/api/v1/arki/deliveries",
        json=_delivery_payload(test_contract.id, test_customer.id),
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )

    today = str(date.today())
    response = await client.get(
        "/api/v1/arki/deliveries",
        params={"delivery_date": today},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    for delivery in data["data"]:
        assert delivery["delivery_date"] == today


async def test_list_deliveries_unauthenticated(client: AsyncClient):
    """인증 없이 목록 조회 → 401"""
    response = await client.get("/api/v1/arki/deliveries")
    assert response.status_code == 401


# ==================== POST /api/v1/arki/deliveries ====================


async def test_create_delivery_success(
    client: AsyncClient,
    auth_headers: dict,
    test_contract: Contract,
    test_customer: Customer,
    test_slot: CapacitySlot,
):
    """배달 생성 성공 (슬롯 존재) → 201"""
    idem_key = f"delivery-create-{uuid.uuid4().hex}"
    response = await client.post(
        "/api/v1/arki/deliveries",
        json=_delivery_payload(test_contract.id, test_customer.id),
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["contract_id"] == str(test_contract.id)
    assert data["data"]["delivery_status"] == "scheduled"
    assert data["data"]["delivery_team"] == "배달팀A"
    assert "id" in data["data"]


async def test_create_delivery_no_capacity_slot_409(
    client: AsyncClient,
    auth_headers: dict,
    test_contract: Contract,
    test_customer: Customer,
):
    """슬롯 없을 때 배달 생성 → 409 CapacityConflict"""
    idem_key = f"delivery-no-slot-{uuid.uuid4().hex}"
    response = await client.post(
        "/api/v1/arki/deliveries",
        json=_delivery_payload(
            test_contract.id,
            test_customer.id,
            delivery_team="존재하지않는팀",
            time_slot="00:00-01:00",
        ),
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "DELIVERY_SLOT_CONFLICT"


async def test_create_delivery_full_slot_409(
    client: AsyncClient,
    auth_headers: dict,
    test_contract: Contract,
    test_customer: Customer,
    test_full_slot: CapacitySlot,
):
    """꽉 찬 슬롯에 배달 생성 → 409"""
    idem_key = f"delivery-full-slot-{uuid.uuid4().hex}"
    response = await client.post(
        "/api/v1/arki/deliveries",
        json=_delivery_payload(
            test_contract.id,
            test_customer.id,
            delivery_team="배달팀B",
            time_slot="13:00-17:00",
        ),
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert response.status_code == 409
    data = response.json()
    assert data["error"]["code"] == "DELIVERY_SLOT_CONFLICT"


async def test_create_delivery_idempotency_conflict(
    client: AsyncClient,
    auth_headers: dict,
    test_contract: Contract,
    test_customer: Customer,
    test_slot: CapacitySlot,
):
    """동일 Idempotency-Key로 두 번 배달 생성 → 409"""
    idem_key = f"delivery-idem-{uuid.uuid4().hex}"
    payload = _delivery_payload(test_contract.id, test_customer.id)

    r1 = await client.post(
        "/api/v1/arki/deliveries",
        json=payload,
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert r1.status_code == 201

    r2 = await client.post(
        "/api/v1/arki/deliveries",
        json=payload,
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "IDEMPOTENCY_CONFLICT"


async def test_create_delivery_missing_idempotency_key(
    client: AsyncClient,
    auth_headers: dict,
    test_contract: Contract,
    test_customer: Customer,
):
    """Idempotency-Key 헤더 누락 → 422"""
    response = await client.post(
        "/api/v1/arki/deliveries",
        json=_delivery_payload(test_contract.id, test_customer.id),
        headers=auth_headers,
    )
    assert response.status_code == 422


# ==================== PATCH /api/v1/arki/deliveries/{id} ====================


async def _create_delivery(
    client: AsyncClient,
    auth_headers: dict,
    contract_id: uuid.UUID,
    customer_id: uuid.UUID,
) -> str:
    """배달 생성 헬퍼 → delivery_id 반환"""
    idem_key = f"helper-{uuid.uuid4().hex}"
    resp = await client.post(
        "/api/v1/arki/deliveries",
        json=_delivery_payload(contract_id, customer_id),
        headers={**auth_headers, "Idempotency-Key": idem_key},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


async def test_update_delivery_valid_transition(
    client: AsyncClient,
    auth_headers: dict,
    test_contract: Contract,
    test_customer: Customer,
    test_slot: CapacitySlot,
):
    """scheduled → confirmed 유효한 상태 전이 → 200"""
    delivery_id = await _create_delivery(
        client, auth_headers, test_contract.id, test_customer.id
    )

    response = await client.patch(
        f"/api/v1/arki/deliveries/{delivery_id}",
        json={"delivery_status": "confirmed"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["delivery_status"] == "confirmed"


async def test_update_delivery_invalid_transition_422(
    client: AsyncClient,
    auth_headers: dict,
    test_contract: Contract,
    test_customer: Customer,
    test_slot: CapacitySlot,
    db_session,
):
    """completed → cancelled 허용되지 않는 전이 → 422"""
    # DB에 직접 completed 상태 배달 생성
    delivery = Delivery(
        id=uuid.uuid4(),
        contract_id=test_contract.id,
        customer_id=test_customer.id,
        delivery_date=date.today(),
        time_slot="09:00-12:00",
        delivery_team="배달팀A",
        address_text="서울시 강남구 테스트로 123",
        delivery_status=DeliveryStatus.completed,
        idempotency_key=f"completed-{uuid.uuid4().hex}",
    )
    db_session.add(delivery)
    await db_session.flush()

    response = await client.patch(
        f"/api/v1/arki/deliveries/{delivery.id}",
        json={"delivery_status": "cancelled"},
        headers=auth_headers,
    )
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_STATUS_TRANSITION"


async def test_update_delivery_not_found(client: AsyncClient, auth_headers: dict):
    """존재하지 않는 배달 수정 → 404"""
    fake_id = uuid.uuid4()
    response = await client.patch(
        f"/api/v1/arki/deliveries/{fake_id}",
        json={"delivery_status": "confirmed"},
        headers=auth_headers,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "DELIVERY_NOT_FOUND"


async def test_update_delivery_multi_step_transition(
    client: AsyncClient,
    auth_headers: dict,
    test_contract: Contract,
    test_customer: Customer,
    test_slot: CapacitySlot,
):
    """scheduled → confirmed → in_transit 연속 전이"""
    delivery_id = await _create_delivery(
        client, auth_headers, test_contract.id, test_customer.id
    )

    # scheduled → confirmed
    r1 = await client.patch(
        f"/api/v1/arki/deliveries/{delivery_id}",
        json={"delivery_status": "confirmed"},
        headers=auth_headers,
    )
    assert r1.status_code == 200
    assert r1.json()["data"]["delivery_status"] == "confirmed"

    # confirmed → in_transit
    r2 = await client.patch(
        f"/api/v1/arki/deliveries/{delivery_id}",
        json={"delivery_status": "in_transit"},
        headers=auth_headers,
    )
    assert r2.status_code == 200
    assert r2.json()["data"]["delivery_status"] == "in_transit"
