"""
UNI-PASS 통관조회 API 클라이언트
Mock/Real 교체 가능 구조
실 연동: Phase 6 / 현재: Mock-only
"""
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class CustomsStatusResult:
    bl_number: str
    customs_status: str
    customs_code: str
    declaration_number: str | None
    arrival_port: str
    cleared_at: str | None
    remarks: str


@dataclass
class ImportDeclarationResult:
    declaration_number: str
    bl_number: str
    importer_name: str
    item_description: str
    quantity: float
    weight_kg: float
    declared_value: float
    currency: str
    duty_amount: float
    vat_amount: float
    status: str
    declared_at: str


class BaseCustomsClient(ABC):
    """UNI-PASS 통관조회 클라이언트 추상 베이스"""

    @abstractmethod
    async def get_customs_status(self, bl_number: str) -> CustomsStatusResult:
        ...

    @abstractmethod
    async def get_import_declaration(
        self, declaration_number: str
    ) -> ImportDeclarationResult:
        ...


class CustomsMockClient(BaseCustomsClient):
    """테스트/개발용 Mock — 실제 API 호출 없음"""

    def __init__(self, config: dict[str, Any] | None = None):
        self._config = config or {}

    async def get_customs_status(self, bl_number: str) -> CustomsStatusResult:
        return CustomsStatusResult(
            bl_number=bl_number,
            customs_status="통관완료",
            customs_code="C04",
            declaration_number="12345-26-000789X",
            arrival_port="인천항",
            cleared_at="2026-03-10T16:45:00+09:00",
            remarks="정상 통관 처리 완료",
        )

    async def get_import_declaration(
        self, declaration_number: str
    ) -> ImportDeclarationResult:
        return ImportDeclarationResult(
            declaration_number=declaration_number,
            bl_number="MSKU1234567890",
            importer_name="(주)아르키스토어",
            item_description="사무용 가구 (시스템 책상, 의자 세트)",
            quantity=120.0,
            weight_kg=3500.0,
            declared_value=28500000.0,
            currency="KRW",
            duty_amount=2280000.0,
            vat_amount=3078000.0,
            status="수리",
            declared_at="2026-03-08T09:30:00+09:00",
        )


class CustomsRealClient(BaseCustomsClient):
    """실제 UNI-PASS 통관조회 API 연동 (Phase 6에서 구현)"""

    # TODO: UNI-PASS Open API 엔드포인트
    # 공식 문서: https://unipass.customs.go.kr/csp/index.do
    BASE_URL = "https://unipass.customs.go.kr:38010/ext/rest"

    def __init__(self, config: dict[str, Any] | None = None):
        self._config = config or {}
        self._api_key = os.getenv("UNIPASS_API_KEY", "")

    async def get_customs_status(self, bl_number: str) -> CustomsStatusResult:
        # TODO: implement — GET {BASE_URL}/cargCsclPrgsInfoQry
        # 화물통관진행정보 조회 API
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/cargCsclPrgsInfoQry",
                params={
                    "crkyCn": self._api_key,
                    "blYy": bl_number[:4] if len(bl_number) >= 4 else "",
                    "blNo": bl_number,
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            item = data.get("cargCsclPrgsInfoQryRsltVo", {})
            return CustomsStatusResult(
                bl_number=bl_number,
                customs_status=item.get("csclPrgsStts", ""),
                customs_code=item.get("csclPrgsSttsCd", ""),
                declaration_number=item.get("dclrNo"),
                arrival_port=item.get("ldprNm", ""),
                cleared_at=item.get("csclEndDttm"),
                remarks=item.get("rmrk", ""),
            )

    async def get_import_declaration(
        self, declaration_number: str
    ) -> ImportDeclarationResult:
        # TODO: implement — GET {BASE_URL}/expDclrNoPrgsInfoQry
        # 수입신고번호 진행정보 조회 API
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/expDclrNoPrgsInfoQry",
                params={
                    "crkyCn": self._api_key,
                    "dclrNo": declaration_number,
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            item = data.get("expDclrNoPrgsInfoQryRsltVo", {})
            return ImportDeclarationResult(
                declaration_number=declaration_number,
                bl_number=item.get("blNo", ""),
                importer_name=item.get("ntprNm", ""),
                item_description=item.get("prnm", ""),
                quantity=float(item.get("qty", 0)),
                weight_kg=float(item.get("wght", 0)),
                declared_value=float(item.get("dclrPrc", 0)),
                currency=item.get("crcy", "KRW"),
                duty_amount=float(item.get("csAmt", 0)),
                vat_amount=float(item.get("vatAmt", 0)),
                status=item.get("csclPrgsStts", ""),
                declared_at=item.get("dclrDttm", ""),
            )


def get_customs_client(
    config: dict[str, Any] | None = None,
) -> BaseCustomsClient:
    """
    의존성 주입용 팩토리
    USE_MOCK_CUSTOMS=true(기본값) → Mock, false → Real
    """
    use_mock = os.getenv("USE_MOCK_CUSTOMS", "true").lower() == "true"
    if use_mock:
        return CustomsMockClient(config=config)
    return CustomsRealClient(config=config)
