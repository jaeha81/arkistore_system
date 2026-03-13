"""
Nine United (배송 포털) API 클라이언트
Mock/Real 교체 가능 구조
실 연동: Phase 6 / 현재: Mock-only
"""
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class NineUnitedDeliveryStatus:
    delivery_id: str
    status: str
    driver_name: str
    driver_phone: str
    vehicle_number: str
    estimated_time: str
    completed_at: str | None


@dataclass
class NineUnitedDeliveryOrderResult:
    order_id: str
    delivery_id: str
    created_at: str
    status: str


@dataclass
class NineUnitedCancelResult:
    delivery_id: str
    cancelled: bool
    cancelled_at: str


class BaseNineUnitedClient(ABC):
    """Nine United 배송 포털 클라이언트 추상 베이스"""

    @abstractmethod
    async def get_delivery_status(
        self, delivery_id: str
    ) -> NineUnitedDeliveryStatus:
        ...

    @abstractmethod
    async def create_delivery_order(
        self, delivery_data: dict[str, Any]
    ) -> NineUnitedDeliveryOrderResult:
        ...

    @abstractmethod
    async def cancel_delivery(self, delivery_id: str) -> NineUnitedCancelResult:
        ...


class NineUnitedMockClient(BaseNineUnitedClient):
    """테스트/개발용 Mock — 실제 API 호출 없음"""

    def __init__(self, config: dict[str, Any] | None = None):
        self._config = config or {}

    async def get_delivery_status(
        self, delivery_id: str
    ) -> NineUnitedDeliveryStatus:
        return NineUnitedDeliveryStatus(
            delivery_id=delivery_id,
            status="in_transit",
            driver_name="이철수",
            driver_phone="010-9876-5432",
            vehicle_number="서울 12가 3456",
            estimated_time="2026-03-12T14:30:00+09:00",
            completed_at=None,
        )

    async def create_delivery_order(
        self, delivery_data: dict[str, Any]
    ) -> NineUnitedDeliveryOrderResult:
        return NineUnitedDeliveryOrderResult(
            order_id="NU-2026-08871",
            delivery_id=delivery_data.get("delivery_id", "DLV-000001"),
            created_at="2026-03-12T09:00:00+09:00",
            status="accepted",
        )

    async def cancel_delivery(self, delivery_id: str) -> NineUnitedCancelResult:
        return NineUnitedCancelResult(
            delivery_id=delivery_id,
            cancelled=True,
            cancelled_at="2026-03-12T10:30:00+09:00",
        )


class NineUnitedRealClient(BaseNineUnitedClient):
    """실제 Nine United 배송 포털 API 연동 (Phase 6에서 구현)"""

    # TODO: Nine United 포털 API 엔드포인트 확인 후 교체
    BASE_URL = "https://api.nineunited.co.kr/v1"

    def __init__(self, config: dict[str, Any] | None = None):
        self._config = config or {}
        self._api_key = os.getenv("NINE_UNITED_API_KEY", "")
        self._partner_code = os.getenv("NINE_UNITED_PARTNER_CODE", "")
        self._headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self._api_key,
            "X-Partner-Code": self._partner_code,
        }

    async def get_delivery_status(
        self, delivery_id: str
    ) -> NineUnitedDeliveryStatus:
        # TODO: implement — GET {BASE_URL}/deliveries/{delivery_id}/status
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/deliveries/{delivery_id}/status",
                headers=self._headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return NineUnitedDeliveryStatus(
                delivery_id=delivery_id,
                status=data["status"],
                driver_name=data.get("driver_name", ""),
                driver_phone=data.get("driver_phone", ""),
                vehicle_number=data.get("vehicle_number", ""),
                estimated_time=data.get("estimated_time", ""),
                completed_at=data.get("completed_at"),
            )

    async def create_delivery_order(
        self, delivery_data: dict[str, Any]
    ) -> NineUnitedDeliveryOrderResult:
        # TODO: implement — POST {BASE_URL}/deliveries
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/deliveries",
                json=delivery_data,
                headers=self._headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return NineUnitedDeliveryOrderResult(
                order_id=data["order_id"],
                delivery_id=data["delivery_id"],
                created_at=data["created_at"],
                status=data["status"],
            )

    async def cancel_delivery(self, delivery_id: str) -> NineUnitedCancelResult:
        # TODO: implement — DELETE {BASE_URL}/deliveries/{delivery_id}
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{self.BASE_URL}/deliveries/{delivery_id}",
                headers=self._headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return NineUnitedCancelResult(
                delivery_id=delivery_id,
                cancelled=data.get("cancelled", True),
                cancelled_at=data.get("cancelled_at", ""),
            )


def get_nine_united_client(
    config: dict[str, Any] | None = None,
) -> BaseNineUnitedClient:
    """
    의존성 주입용 팩토리
    USE_MOCK_NINE_UNITED=true(기본값) → Mock, false → Real
    """
    use_mock = os.getenv("USE_MOCK_NINE_UNITED", "true").lower() == "true"
    if use_mock:
        return NineUnitedMockClient(config=config)
    return NineUnitedRealClient(config=config)
