"""
공통 응답 Envelope
모든 API 응답은 이 형식을 따른다:
{
    "success": true/false,
    "data": {...} or [...],
    "meta": {
        "request_id": "...",
        "timestamp": "...",
        "page": 1,        # 목록 조회 시
        "page_size": 20,  # 목록 조회 시
        "total": 100,     # 목록 조회 시
    },
    "error": {            # 오류 시만
        "code": "...",
        "message": "...",
        "details": null,
        "trace_id": "..."
    }
}
"""
from datetime import datetime, timezone
from typing import Any, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MetaSchema(BaseModel):
    request_id: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PaginationMetaSchema(MetaSchema):
    page: int = 1
    page_size: int = 20
    total: int = 0


class ErrorDetailSchema(BaseModel):
    code: str
    message: str
    details: Any = None
    trace_id: str | None = None


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any
    meta: MetaSchema = Field(default_factory=MetaSchema)


class PaginatedResponse(BaseModel):
    success: bool = True
    data: list[Any]
    meta: PaginationMetaSchema = Field(default_factory=PaginationMetaSchema)


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetailSchema
    meta: MetaSchema = Field(default_factory=MetaSchema)


def success_response(
    data: Any,
    request_id: str | None = None,
) -> dict:
    return {
        "success": True,
        "data": data,
        "meta": {
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }


def paginated_response(
    data: list,
    page: int,
    page_size: int,
    total: int,
    request_id: str | None = None,
) -> dict:
    return {
        "success": True,
        "data": data,
        "meta": {
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "page": page,
            "page_size": page_size,
            "total": total,
        },
    }


def error_response(
    code: str,
    message: str,
    details: Any = None,
    trace_id: str | None = None,
    request_id: str | None = None,
) -> dict:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "trace_id": trace_id,
        },
        "meta": {
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
