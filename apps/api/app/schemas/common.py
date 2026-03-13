"""
공통 응답 스키마 - app.core.responses 재export + Generic 타입 래퍼
"""
from app.core.responses import (
    ErrorDetailSchema,
    ErrorResponse,
    MetaSchema,
    PaginatedResponse,
    PaginationMetaSchema,
    SuccessResponse,
    error_response,
    paginated_response,
    success_response,
)

__all__ = [
    "MetaSchema",
    "PaginationMetaSchema",
    "ErrorDetailSchema",
    "SuccessResponse",
    "PaginatedResponse",
    "ErrorResponse",
    "success_response",
    "paginated_response",
    "error_response",
]
