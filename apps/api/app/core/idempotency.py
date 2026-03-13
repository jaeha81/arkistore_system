"""
Idempotency-Key 기반 중복 요청 방지
대상 API: contracts, purchase_requests, purchase_orders, deliveries,
          error_reports, github_issues, sheet_sync_jobs
"""
import json
from typing import Any

from fastapi import Header, HTTPException, Request, status


class IdempotencyStore:
    """
    In-memory store (MVP 용)
    Phase 2에서 Redis로 교체
    """
    _store: dict[str, dict] = {}

    def get(self, key: str) -> dict | None:
        return self._store.get(key)

    def set(self, key: str, value: dict) -> None:
        self._store[key] = value

    def exists(self, key: str) -> bool:
        return key in self._store


_store = IdempotencyStore()


async def check_idempotency(
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
) -> str:
    """
    FastAPI Dependency
    중복 키 감지 시 기존 응답 반환
    """
    # 요청 경로 + 키 조합으로 저장
    store_key = f"{request.method}:{request.url.path}:{idempotency_key}"

    existing = _store.get(store_key)
    if existing:
        raise IdempotencyReplayException(
            cached_response=existing["response"],
            status_code=existing["status_code"],
        )

    # key를 request.state에 저장 (서비스에서 사용)
    request.state.idempotency_key = store_key
    return store_key


def save_idempotency_response(
    store_key: str,
    response_data: Any,
    status_code: int,
) -> None:
    """응답 저장 (라우터에서 호출)"""
    _store.set(store_key, {
        "response": response_data,
        "status_code": status_code,
    })


class IdempotencyReplayException(Exception):
    """중복 요청 감지 - 기존 응답 재사용"""

    def __init__(self, cached_response: Any, status_code: int):
        self.cached_response = cached_response
        self.status_code = status_code
