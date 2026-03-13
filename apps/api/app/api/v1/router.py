"""
API v1 메인 라우터
모든 도메인 라우터를 통합 등록
"""
from fastapi import APIRouter

from app.api.v1 import (
    auth,
    capacity_slots,
    consultations,
    contracts,
    customers,
    dashboard,
    deliveries,
    error_reports,
    files,
    happy_calls,
    inventory,
    invoices,
    leads,
    ops_issues,
    ops_logs,
    ops_projects,
    products,
    purchase_orders,
    purchase_requests,
    shipments,
    sync,
)

# main.py에서 prefix 없이 include하므로 여기서 prefix 설정하지 않음
api_router = APIRouter()

# ==================== 인증 ====================
api_router.include_router(auth.router)

# ==================== 운영 도메인 ====================
api_router.include_router(ops_projects.router)
api_router.include_router(ops_issues.router)
api_router.include_router(ops_logs.router)

# ==================== 업무 도메인 ====================
api_router.include_router(dashboard.router)
api_router.include_router(products.router)
api_router.include_router(inventory.router)
api_router.include_router(customers.router)
api_router.include_router(leads.router)
api_router.include_router(consultations.router)
api_router.include_router(contracts.router)
api_router.include_router(purchase_requests.router)
api_router.include_router(purchase_orders.router)
api_router.include_router(invoices.router)
api_router.include_router(shipments.router)
api_router.include_router(deliveries.router)
api_router.include_router(capacity_slots.router)
api_router.include_router(happy_calls.router)

# ==================== 에러 리포트 ====================
api_router.include_router(error_reports.router)

# ==================== 공통 ====================
api_router.include_router(files.router)
api_router.include_router(sync.router)
