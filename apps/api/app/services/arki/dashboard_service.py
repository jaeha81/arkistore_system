"""
대시보드 서비스 (업무 도메인)
각종 집계 데이터 조회
"""
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import (
    DeliveryStatus,
    InventoryStatus,
    IssueStatus,
    LeadStatus,
    PurchaseRequestStatus,
)
from app.models.capacity_slot import CapacitySlot
from app.models.delivery import Delivery
from app.models.error_report import ErrorReport
from app.models.inventory import Inventory
from app.models.lead import Lead
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_request import PurchaseRequest


async def get_summary(db: AsyncSession) -> dict[str, Any]:
    """대시보드 요약 데이터 집계"""
    today = date.today()

    # 발주 총 건수
    orders_total = (
        await db.execute(select(func.count()).select_from(PurchaseOrder))
    ).scalar() or 0

    # 구매요청 대기
    purchase_requests_pending = (
        await db.execute(
            select(func.count())
            .select_from(PurchaseRequest)
            .where(PurchaseRequest.request_status == PurchaseRequestStatus.requested)
        )
    ).scalar() or 0

    # 재고 부족
    low_stock_count = (
        await db.execute(
            select(func.count())
            .select_from(Inventory)
            .where(
                Inventory.inventory_status.in_([
                    InventoryStatus.low_stock,
                    InventoryStatus.out_of_stock,
                ])
            )
        )
    ).scalar() or 0

    # 신규 문의
    new_inquiries_count = (
        await db.execute(
            select(func.count())
            .select_from(Lead)
            .where(Lead.lead_status == LeadStatus.new)
        )
    ).scalar() or 0

    # 오늘 배송 건수
    deliveries_today = (
        await db.execute(
            select(func.count())
            .select_from(Delivery)
            .where(Delivery.delivery_date == today)
        )
    ).scalar() or 0

    # 오늘 CAPA 잔여
    capa_remaining_today = (
        await db.execute(
            select(func.coalesce(func.sum(CapacitySlot.remaining_capacity), 0))
            .where(CapacitySlot.slot_date == today)
        )
    ).scalar() or 0

    # 미해결 이슈
    open_issue_count = (
        await db.execute(
            select(func.count())
            .select_from(ErrorReport)
            .where(ErrorReport.report_status == IssueStatus.new)
        )
    ).scalar() or 0

    return {
        "orders_total": orders_total,
        "purchase_requests_pending": purchase_requests_pending,
        "low_stock_count": low_stock_count,
        "new_inquiries_count": new_inquiries_count,
        "deliveries_today": deliveries_today,
        "capa_remaining_today": capa_remaining_today,
        "open_issue_count": open_issue_count,
    }
