"""
Google Sheets API v4 클라이언트 래퍼
서비스 계정(Service Account) 인증 기반
실 연동: Phase 6 / 현재: Mock 구조
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SheetWritePayload:
    spreadsheet_id: str
    sheet_name: str
    rows: list[list[Any]]  # 헤더 포함 2D 배열
    start_range: str = "A1"


@dataclass
class SheetReadResult:
    values: list[list[Any]] = field(default_factory=list)
    row_count: int = 0


class BaseGoogleSheetsClient(ABC):
    @abstractmethod
    async def write_rows(self, payload: SheetWritePayload) -> bool:
        ...

    @abstractmethod
    async def read_range(
        self, spreadsheet_id: str, range_name: str
    ) -> SheetReadResult:
        ...

    @abstractmethod
    async def clear_range(self, spreadsheet_id: str, range_name: str) -> bool:
        ...


class GoogleSheetsClient(BaseGoogleSheetsClient):
    """실제 Google Sheets API v4 연동 (Phase 6에서 구현)"""

    def __init__(self, service_account_json: str):
        # 실 구현 시: google-auth + google-api-python-client 사용
        self._service_account_json = service_account_json
        self._service = None  # lazy init

    def _get_service(self):
        if self._service is None:
            import json

            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            creds_dict = json.loads(self._service_account_json)
            creds = service_account.Credentials.from_service_account_info(
                creds_dict,
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )
            self._service = build("sheets", "v4", credentials=creds)
        return self._service

    async def write_rows(self, payload: SheetWritePayload) -> bool:
        service = self._get_service()
        range_name = f"{payload.sheet_name}!{payload.start_range}"
        body = {"values": payload.rows}
        service.spreadsheets().values().update(
            spreadsheetId=payload.spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()
        return True

    async def read_range(
        self, spreadsheet_id: str, range_name: str
    ) -> SheetReadResult:
        service = self._get_service()
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        values = result.get("values", [])
        return SheetReadResult(values=values, row_count=len(values))

    async def clear_range(self, spreadsheet_id: str, range_name: str) -> bool:
        service = self._get_service()
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id, range=range_name
        ).execute()
        return True


class MockGoogleSheetsClient(BaseGoogleSheetsClient):
    """테스트/개발용 Mock"""

    async def write_rows(self, payload: SheetWritePayload) -> bool:
        print(f"[MOCK] Write {len(payload.rows)} rows to {payload.sheet_name}")
        return True

    async def read_range(
        self, spreadsheet_id: str, range_name: str
    ) -> SheetReadResult:
        return SheetReadResult(values=[], row_count=0)

    async def clear_range(self, spreadsheet_id: str, range_name: str) -> bool:
        return True


def get_sheets_client() -> BaseGoogleSheetsClient:
    from app.core.config import settings

    if settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        return GoogleSheetsClient(
            service_account_json=settings.GOOGLE_SERVICE_ACCOUNT_JSON
        )
    return MockGoogleSheetsClient()
