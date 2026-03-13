"""
Ecount ERP API 클라이언트
Mock/Real 교체 가능 구조
실 연동: Phase 6 / 현재: Mock-only
"""
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import httpx


@dataclass
class EcountProductResult:
    product_code: str
    product_name: str
    category_name: str
    unit_price: float
    currency: str
    supplier_name: str
    is_active: bool


@dataclass
class EcountInventorySyncResult:
    product_code: str
    synced_quantity: float
    warehouse_name: str
    sync_success: bool


@dataclass
class EcountCustomerResult:
    customer_code: str
    customer_name: str
    contact_name: str
    phone: str
    email: str
    address: str


@dataclass
class EcountSalesOrderResult:
    order_number: str
    order_date: str
    total_amount: float
    status: str


class BaseEcountClient(ABC):
    """Ecount ERP 클라이언트 추상 베이스"""

    @abstractmethod
    async def get_product(self, product_code: str) -> EcountProductResult:
        ...

    @abstractmethod
    async def sync_inventory(
        self, product_code: str, quantity: float
    ) -> EcountInventorySyncResult:
        ...

    @abstractmethod
    async def get_customer(self, customer_code: str) -> EcountCustomerResult:
        ...

    @abstractmethod
    async def create_sales_order(
        self, order_data: dict[str, Any]
    ) -> EcountSalesOrderResult:
        ...


class EcountMockClient(BaseEcountClient):
    """테스트/개발용 Mock — 실제 API 호출 없음"""

    def __init__(self, config: dict[str, Any] | None = None):
        self._config = config or {}

    async def get_product(self, product_code: str) -> EcountProductResult:
        return EcountProductResult(
            product_code=product_code,
            product_name="아르키스토어 시스템 책상 1200",
            category_name="가구/사무용",
            unit_price=245000.0,
            currency="KRW",
            supplier_name="(주)한샘퍼니처",
            is_active=True,
        )

    async def sync_inventory(
        self, product_code: str, quantity: float
    ) -> EcountInventorySyncResult:
        return EcountInventorySyncResult(
            product_code=product_code,
            synced_quantity=quantity,
            warehouse_name="서울 본사 창고",
            sync_success=True,
        )

    async def get_customer(self, customer_code: str) -> EcountCustomerResult:
        return EcountCustomerResult(
            customer_code=customer_code,
            customer_name="(주)디자인하우스",
            contact_name="김영수",
            phone="02-1234-5678",
            email="kim@designhouse.co.kr",
            address="서울특별시 강남구 역삼동 123-45",
        )

    async def create_sales_order(
        self, order_data: dict[str, Any]
    ) -> EcountSalesOrderResult:
        return EcountSalesOrderResult(
            order_number="SO-2026-00142",
            order_date="2026-03-12",
            total_amount=order_data.get("total_amount", 1500000.0),
            status="created",
        )


class EcountRealClient(BaseEcountClient):
    """실제 Ecount ERP API 연동 (Phase 6에서 구현)"""

    # TODO: Ecount API 엔드포인트 확인 후 교체
    BASE_URL = "https://oapi.ecount.com/OAPI/V2"

    def __init__(self, config: dict[str, Any] | None = None):
        self._config = config or {}
        self._api_key = os.getenv("ECOUNT_API_KEY", "")
        self._company_code = os.getenv("ECOUNT_COMPANY_CODE", "")
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }

    async def get_product(self, product_code: str) -> EcountProductResult:
        # TODO: implement — GET {BASE_URL}/InventoryBasic/GetListInventoryBasic
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/InventoryBasic/GetListInventoryBasic",
                params={"PROD_CD": product_code, "COM_CODE": self._company_code},
                headers=self._headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            item = data["Data"]["Rows"][0]
            return EcountProductResult(
                product_code=item["PROD_CD"],
                product_name=item["PROD_DES"],
                category_name=item.get("CLASS_CD", ""),
                unit_price=float(item.get("PRICE", 0)),
                currency="KRW",
                supplier_name=item.get("CUST_DES", ""),
                is_active=True,
            )

    async def sync_inventory(
        self, product_code: str, quantity: float
    ) -> EcountInventorySyncResult:
        # TODO: implement — POST {BASE_URL}/InventoryBasic/SaveInventoryBasic
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/InventoryBasic/SaveInventoryBasic",
                json={
                    "COM_CODE": self._company_code,
                    "PROD_CD": product_code,
                    "QTY": quantity,
                },
                headers=self._headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            return EcountInventorySyncResult(
                product_code=product_code,
                synced_quantity=quantity,
                warehouse_name="",
                sync_success=True,
            )

    async def get_customer(self, customer_code: str) -> EcountCustomerResult:
        # TODO: implement — GET {BASE_URL}/AccountBasic/GetListAccountBasic
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/AccountBasic/GetListAccountBasic",
                params={"CUST_CD": customer_code, "COM_CODE": self._company_code},
                headers=self._headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            item = data["Data"]["Rows"][0]
            return EcountCustomerResult(
                customer_code=item["CUST_CD"],
                customer_name=item["CUST_DES"],
                contact_name=item.get("CONTACT_NM", ""),
                phone=item.get("TEL_NO", ""),
                email=item.get("EMAIL", ""),
                address=item.get("ADDR", ""),
            )

    async def create_sales_order(
        self, order_data: dict[str, Any]
    ) -> EcountSalesOrderResult:
        # TODO: implement — POST {BASE_URL}/Sale/SaveSale
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/Sale/SaveSale",
                json={
                    "COM_CODE": self._company_code,
                    **order_data,
                },
                headers=self._headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return EcountSalesOrderResult(
                order_number=data["Data"]["IO_NO"],
                order_date=data["Data"]["IO_DATE"],
                total_amount=float(data["Data"].get("SUPPLY_AMT", 0)),
                status="created",
            )


def get_ecount_client(config: dict[str, Any] | None = None) -> BaseEcountClient:
    """
    의존성 주입용 팩토리
    USE_MOCK_ECOUNT=true(기본값) → Mock, false → Real
    """
    use_mock = os.getenv("USE_MOCK_ECOUNT", "true").lower() == "true"
    if use_mock:
        return EcountMockClient(config=config)
    return EcountRealClient(config=config)
