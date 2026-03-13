"""
전체 시스템 커스텀 예외 클래스
모든 도메인 예외는 이 파일에서 정의한다
"""
from typing import Any


class AppException(Exception):
    """기본 애플리케이션 예외"""
    code: str = "APP_ERROR"
    message: str = "Unexpected application error"
    status_code: int = 500

    def __init__(self, message: str | None = None, details: Any = None):
        self.message = message or self.__class__.message
        self.details = details
        super().__init__(self.message)


class NotFoundException(AppException):
    code = "RESOURCE_NOT_FOUND"
    message = "Resource not found"
    status_code = 404


class PermissionDeniedException(AppException):
    code = "PERMISSION_DENIED"
    message = "Permission denied"
    status_code = 403


class UnauthorizedException(AppException):
    code = "UNAUTHORIZED"
    message = "Authentication required"
    status_code = 401


class ValidationException(AppException):
    code = "VALIDATION_ERROR"
    message = "Validation error"
    status_code = 422


class ConflictException(AppException):
    code = "RESOURCE_CONFLICT"
    message = "Resource conflict"
    status_code = 409


class IdempotencyConflictException(AppException):
    code = "IDEMPOTENCY_CONFLICT"
    message = "Duplicate request detected"
    status_code = 409


# ==================== 업무 도메인 예외 ====================

class CapacityConflictException(AppException):
    code = "DELIVERY_SLOT_CONFLICT"
    message = "Delivery slot is full or unavailable"
    status_code = 409


class InvalidStatusTransitionException(AppException):
    code = "INVALID_STATUS_TRANSITION"
    message = "Invalid status transition"
    status_code = 422


class ContractNotFoundException(NotFoundException):
    code = "CONTRACT_NOT_FOUND"
    message = "Contract not found"


class CustomerNotFoundException(NotFoundException):
    code = "CUSTOMER_NOT_FOUND"
    message = "Customer not found"


class ProductNotFoundException(NotFoundException):
    code = "PRODUCT_NOT_FOUND"
    message = "Product not found"


class PurchaseRequestNotFoundException(NotFoundException):
    code = "PURCHASE_REQUEST_NOT_FOUND"
    message = "Purchase request not found"


class PurchaseOrderNotFoundException(NotFoundException):
    code = "PURCHASE_ORDER_NOT_FOUND"
    message = "Purchase order not found"


class DeliveryNotFoundException(NotFoundException):
    code = "DELIVERY_NOT_FOUND"
    message = "Delivery not found"


# ==================== 운영 도메인 예외 ====================

class ProjectNotFoundException(NotFoundException):
    code = "PROJECT_NOT_FOUND"
    message = "Project not found"


class IssueNotFoundException(NotFoundException):
    code = "ISSUE_NOT_FOUND"
    message = "Issue not found"


class IssueDuplicateGroupedException(AppException):
    code = "ISSUE_DUPLICATE_GROUPED"
    message = "Issue already grouped"
    status_code = 409


class GithubIntegrationException(AppException):
    code = "GITHUB_INTEGRATION_ERROR"
    message = "GitHub integration error"
    status_code = 502


# ==================== 외부 연동 예외 ====================

class ExternalIntegrationException(AppException):
    code = "EXTERNAL_INTEGRATION_ERROR"
    message = "External integration error"
    status_code = 502


class StorageException(AppException):
    code = "STORAGE_ERROR"
    message = "File storage error"
    status_code = 502
