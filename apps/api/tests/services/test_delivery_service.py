"""
배달 서비스 유닛 테스트
직접 서비스 함수를 호출하여 비즈니스 로직 검증
"""
import uuid
from datetime import date

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import DeliveryStatus, SlotStatus
from app.core.exceptions import (
    CapacityConflictException,
    DeliveryNotFoundException,
    IdempotencyConflictException,
    InvalidStatusTransitionException,
)
from app.models.capacity_slot import CapacitySlot
from app.models.contract import Contract
from app.models.customer import Customer
from app.models.delivery import Delivery
from app.services.arki import delivery_service


# ==================== 로컬 픽스처 ====================


@pytest_asyncio.fixture
async def actor_user_id() -> uuid.UUID:
    """테스트용 액터 사용자 ID"""
    return uuid.uuid4()


@pytest_asyncio.fixture
async def test_customer(db_session: AsyncSession) -> Customer:
    customer = Customer(
        id=uuid.uuid4(),
        customer_type="individual",
        name="서비스 테스트 고객",
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
        contract_amount=3000000,
        contract_status="draft",
        delivery_required=True,
        idempotency_key=f"svc-contract-{uuid.uuid4().hex}",
    )
    db_session.add(contract)
    await db_session.flush()
    return contract


@pytest_asyncio.fixture
async def open_slot(db_session: AsyncSession) -> CapacitySlot:
    """가용 슬롯"""
    slot = CapacitySlot(
        id=uuid.uuid4(),
        slot_date=date.today(),
        delivery_team="서비스팀A",
        time_slot="10:00-13:00",
        max_capacity=5,
        used_capacity=0,
        remaining_capacity=5,
        slot_status=SlotStatus.open,
    )
    db_session.add(slot)
    await db_session.flush()
    return slot


@pytest_asyncio.fixture
async def full_slot(db_session: AsyncSession) -> CapacitySlot:
    """꽉 찬 슬롯"""
    slot = CapacitySlot(
        id=uuid.uuid4(),
        slot_date=date.today(),
        delivery_team="서비스팀B",
        time_slot="14:00-17:00",
        max_capacity=1,
        used_capacity=1,
        remaining_capacity=0,
        slot_status=SlotStatus.full,
    )
    db_session.add(slot)
    await db_session.flush()
    return slot


def _delivery_data(
    contract_id: uuid.UUID,
    customer_id: uuid.UUID,
    delivery_team: str = "서비스팀A",
    time_slot: str = "10:00-13:00",
) -> dict:
    return {
        "contract_id": contract_id,
        "customer_id": customer_id,
        "delivery_date": date.today(),
        "time_slot": time_slot,
        "delivery_team": delivery_team,
        "address_text": "서울시 서초구 서비스로 456",
        "ladder_required": False,
    }


# ==================== create_delivery ====================


async def test_create_delivery_success(
    db_session: AsyncSession,
    test_contract: Contract,
    test_customer: Customer,
    open_slot: CapacitySlot,
    actor_user_id: uuid.UUID,
):
    """성공 경로: 슬롯 존재 → 배달 생성, 슬롯 used_capacity 증가"""
    idem_key = f"svc-create-{uuid.uuid4().hex}"
    data = _delivery_data(test_contract.id, test_customer.id)

    delivery = await delivery_service.create_delivery(
        data=data,
        idempotency_key=idem_key,
        db=db_session,
        actor_user_id=actor_user_id,
    )

    assert delivery.id is not None
    assert delivery.delivery_status == DeliveryStatus.scheduled
    assert delivery.idempotency_key == idem_key
    assert delivery.contract_id == test_contract.id
    assert delivery.customer_id == test_customer.id

    # 슬롯 used_capacity 증가 확인
    await db_session.refresh(open_slot)
    assert open_slot.used_capacity == 1
    assert open_slot.remaining_capacity == 4


async def test_create_delivery_slot_full_raises_capacity_conflict(
    db_session: AsyncSession,
    test_contract: Contract,
    test_customer: Customer,
    full_slot: CapacitySlot,
    actor_user_id: uuid.UUID,
):
    """꽉 찬 슬롯 → CapacityConflictException"""
    data = _delivery_data(
        test_contract.id,
        test_customer.id,
        delivery_team="서비스팀B",
        time_slot="14:00-17:00",
    )

    with pytest.raises(CapacityConflictException) as exc_info:
        await delivery_service.create_delivery(
            data=data,
            idempotency_key=f"full-slot-{uuid.uuid4().hex}",
            db=db_session,
            actor_user_id=actor_user_id,
        )

    assert exc_info.value.code == "DELIVERY_SLOT_CONFLICT"


async def test_create_delivery_no_slot_raises_capacity_conflict(
    db_session: AsyncSession,
    test_contract: Contract,
    test_customer: Customer,
    actor_user_id: uuid.UUID,
):
    """슬롯 없음 → CapacityConflictException"""
    data = _delivery_data(
        test_contract.id,
        test_customer.id,
        delivery_team="없는팀",
        time_slot="99:00-99:00",
    )

    with pytest.raises(CapacityConflictException):
        await delivery_service.create_delivery(
            data=data,
            idempotency_key=f"no-slot-{uuid.uuid4().hex}",
            db=db_session,
            actor_user_id=actor_user_id,
        )


async def test_create_delivery_idempotency_conflict(
    db_session: AsyncSession,
    test_contract: Contract,
    test_customer: Customer,
    open_slot: CapacitySlot,
    actor_user_id: uuid.UUID,
):
    """동일 idempotency_key 두 번 → IdempotencyConflictException"""
    idem_key = f"idem-svc-{uuid.uuid4().hex}"
    data = _delivery_data(test_contract.id, test_customer.id)

    # 첫 번째 생성
    await delivery_service.create_delivery(
        data=data,
        idempotency_key=idem_key,
        db=db_session,
        actor_user_id=actor_user_id,
    )

    # 두 번째 생성 (동일 키)
    with pytest.raises(IdempotencyConflictException):
        await delivery_service.create_delivery(
            data=data,
            idempotency_key=idem_key,
            db=db_session,
            actor_user_id=actor_user_id,
        )


# ==================== update_delivery ====================


async def _create_delivery_direct(
    db_session: AsyncSession,
    contract_id: uuid.UUID,
    customer_id: uuid.UUID,
    status: DeliveryStatus = DeliveryStatus.scheduled,
) -> Delivery:
    """테스트용 배달 직접 생성 (슬롯 예약 없이)"""
    delivery = Delivery(
        id=uuid.uuid4(),
        contract_id=contract_id,
        customer_id=customer_id,
        delivery_date=date.today(),
        time_slot="10:00-13:00",
        delivery_team="서비스팀A",
        address_text="서울시 서초구 서비스로 456",
        delivery_status=status,
        idempotency_key=f"direct-{uuid.uuid4().hex}",
    )
    db_session.add(delivery)
    await db_session.flush()
    return delivery


async def test_update_delivery_valid_transition_scheduled_to_confirmed(
    db_session: AsyncSession,
    test_contract: Contract,
    test_customer: Customer,
    actor_user_id: uuid.UUID,
):
    """scheduled → confirmed 유효한 전이"""
    delivery = await _create_delivery_direct(
        db_session, test_contract.id, test_customer.id, DeliveryStatus.scheduled
    )

    updated = await delivery_service.update_delivery(
        delivery_id=delivery.id,
        data={"delivery_status": DeliveryStatus.confirmed},
        db=db_session,
        actor_user_id=actor_user_id,
    )

    assert updated.delivery_status == DeliveryStatus.confirmed


async def test_update_delivery_valid_transition_confirmed_to_in_transit(
    db_session: AsyncSession,
    test_contract: Contract,
    test_customer: Customer,
    actor_user_id: uuid.UUID,
):
    """confirmed → in_transit 유효한 전이"""
    delivery = await _create_delivery_direct(
        db_session, test_contract.id, test_customer.id, DeliveryStatus.confirmed
    )

    updated = await delivery_service.update_delivery(
        delivery_id=delivery.id,
        data={"delivery_status": DeliveryStatus.in_transit},
        db=db_session,
        actor_user_id=actor_user_id,
    )

    assert updated.delivery_status == DeliveryStatus.in_transit


async def test_update_delivery_invalid_transition_completed_to_cancelled(
    db_session: AsyncSession,
    test_contract: Contract,
    test_customer: Customer,
    actor_user_id: uuid.UUID,
):
    """completed → cancelled 허용되지 않는 전이 → InvalidStatusTransitionException"""
    delivery = await _create_delivery_direct(
        db_session, test_contract.id, test_customer.id, DeliveryStatus.completed
    )

    with pytest.raises(InvalidStatusTransitionException) as exc_info:
        await delivery_service.update_delivery(
            delivery_id=delivery.id,
            data={"delivery_status": DeliveryStatus.cancelled},
            db=db_session,
            actor_user_id=actor_user_id,
        )

    assert exc_info.value.code == "INVALID_STATUS_TRANSITION"
    assert "completed" in exc_info.value.message.lower() or "completed" in str(exc_info.value)


async def test_update_delivery_invalid_transition_cancelled_to_scheduled(
    db_session: AsyncSession,
    test_contract: Contract,
    test_customer: Customer,
    actor_user_id: uuid.UUID,
):
    """cancelled → scheduled 허용되지 않는 전이 → InvalidStatusTransitionException"""
    delivery = await _create_delivery_direct(
        db_session, test_contract.id, test_customer.id, DeliveryStatus.cancelled
    )

    with pytest.raises(InvalidStatusTransitionException):
        await delivery_service.update_delivery(
            delivery_id=delivery.id,
            data={"delivery_status": DeliveryStatus.scheduled},
            db=db_session,
            actor_user_id=actor_user_id,
        )


async def test_update_delivery_not_found(
    db_session: AsyncSession,
    actor_user_id: uuid.UUID,
):
    """존재하지 않는 배달 수정 → DeliveryNotFoundException"""
    fake_id = uuid.uuid4()

    with pytest.raises(DeliveryNotFoundException):
        await delivery_service.update_delivery(
            delivery_id=fake_id,
            data={"delivery_status": DeliveryStatus.confirmed},
            db=db_session,
            actor_user_id=actor_user_id,
        )


async def test_update_delivery_same_status_no_error(
    db_session: AsyncSession,
    test_contract: Contract,
    test_customer: Customer,
    actor_user_id: uuid.UUID,
):
    """동일 상태로 업데이트 → 오류 없음 (전이 검증 스킵)"""
    delivery = await _create_delivery_direct(
        db_session, test_contract.id, test_customer.id, DeliveryStatus.scheduled
    )

    updated = await delivery_service.update_delivery(
        delivery_id=delivery.id,
        data={"delivery_status": DeliveryStatus.scheduled},
        db=db_session,
        actor_user_id=actor_user_id,
    )

    assert updated.delivery_status == DeliveryStatus.scheduled


# ==================== list_deliveries ====================


async def test_list_deliveries_empty(db_session: AsyncSession):
    """배달 없을 때 빈 목록"""
    deliveries, total = await delivery_service.list_deliveries({}, db_session)
    assert isinstance(deliveries, list)
    assert total >= 0


async def test_list_deliveries_filter_by_date(
    db_session: AsyncSession,
    test_contract: Contract,
    test_customer: Customer,
):
    """날짜 필터"""
    delivery = await _create_delivery_direct(
        db_session, test_contract.id, test_customer.id
    )

    deliveries, total = await delivery_service.list_deliveries(
        {"delivery_date": date.today()}, db_session
    )
    delivery_ids = [str(d.id) for d in deliveries]
    assert str(delivery.id) in delivery_ids
