"""
대시보드 요약 스키마
"""
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    orders_total: int = 0
    purchase_requests_pending: int = 0
    low_stock_count: int = 0
    new_inquiries_count: int = 0
    deliveries_today: int = 0
    capa_remaining_today: int = 0
    open_issue_count: int = 0
