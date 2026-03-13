"""
역할 기반 접근 제어 (RBAC)
FastAPI Dependency로 사용
"""
from fastapi import Depends, HTTPException, status

from app.core.enums import UserRole


def require_roles(*roles: UserRole):
    """특정 역할 중 하나를 요구하는 dependency"""
    def checker(current_user=Depends(get_current_user_placeholder)):
        user_role = current_user.get("role")
        if user_role not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )
        return current_user
    return checker


def get_current_user_placeholder():
    """
    임시 placeholder - auth_service 구현 후 교체
    실제 구현: app/api/deps.py의 get_current_user 사용
    """
    return {}


# 역할별 권한 정의
ROLE_PERMISSIONS: dict[str, list[str]] = {
    UserRole.super_admin: ["*"],  # 전체 권한
    UserRole.ops_admin: [
        "projects:read", "projects:write",
        "issues:read", "issues:write",
        "logs:read",
        "deployments:read", "deployments:write",
        "admin_actions:read",
        "files:write",
        "sync:write",
    ],
    UserRole.arki_logistics: [
        "dashboard:read",
        "products:read", "products:write",
        "inventory:read", "inventory:write",
        "purchase_requests:read", "purchase_requests:write",
        "purchase_orders:read", "purchase_orders:write",
        "invoices:read", "invoices:write",
        "shipments:read", "shipments:write",
        "deliveries:read",
        "capacity_slots:read", "capacity_slots:write",
        "files:write",
        "sync:write",
        "error_reports:write",
    ],
    UserRole.arki_sales: [
        "dashboard:read",
        "customers:read", "customers:write",
        "leads:read", "leads:write",
        "consultations:read", "consultations:write",
        "files:write",
        "sync:write",
        "error_reports:write",
    ],
    UserRole.arki_store_manager: [
        "dashboard:read",
        "customers:read", "customers:write",
        "consultations:read", "consultations:write",
        "contracts:read", "contracts:write",
        "deliveries:read", "deliveries:write",
        "capacity_slots:read",
        "happy_calls:read", "happy_calls:write",
        "files:write",
        "sync:write",
        "error_reports:write",
    ],
    UserRole.support_operator: [
        "issues:read", "issues:write",
        "logs:read",
        "deployments:read",
        "error_reports:write",
    ],
}


def has_permission(role: str, permission: str) -> bool:
    """역할이 특정 권한을 갖는지 확인"""
    perms = ROLE_PERMISSIONS.get(role, [])
    return "*" in perms or permission in perms
