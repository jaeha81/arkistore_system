"""
Nine United Adapter
서비스에서 직접 사용하는 인터페이스
Nine United 배송 포털 ↔ 내부 DB 동기화 담당
"""
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import DeliveryStatus
from app.integrations.nine_united.client import (
    BaseNineUnitedClient,
    get_nine_united_client,
)
from app.models.delivery import Delivery

logger = logging.getLogger(__name__)

_STATUS_MAP: dict[str, DeliveryStatus] = {
    "accepted": DeliveryStatus.confirmed,
    "in_transit": DeliveryStatus.in_transit,
    "delivered": DeliveryStatus.completed,
    "delayed": DeliveryStatus.delayed,
    "cancelled": DeliveryStatus.cancelled,
}


class NineUnitedAdapter:
    """Nine United 배송 포털 연동 어댑터"""

    def __init__(self, client: BaseNineUnitedClient | None = None):
        self.client = client or get_nine_united_client()

    async def push_delivery_to_portal(
        self, delivery_id: str, db: AsyncSession
    ) -> bool:
        """
        내부 배송 정보를 Nine United 포털에 전송하여 배송 오더 생성
        """
        result = await db.execute(
            select(Delivery).where(Delivery.id == delivery_id)
        )
        delivery = result.scalar_one_or_none()

        if delivery is None:
            logger.warning("배송 정보 없음: delivery_id=%s", delivery_id)
            return False

        delivery_data: dict[str, Any] = {
            "delivery_id": str(delivery.id),
            "delivery_number": delivery.delivery_number or "",
            "delivery_date": delivery.delivery_date.isoformat(),
            "time_slot": delivery.time_slot,
            "delivery_team": delivery.delivery_team,
            "vehicle_code": delivery.vehicle_code or "",
            "address": delivery.address_text,
            "ladder_required": delivery.ladder_required,
        }

        order_result = await self.client.create_delivery_order(delivery_data)

        logger.info(
            "DB → Nine United 배송 오더 생성: delivery_id=%s, order_id=%s, status=%s",
            delivery_id,
            order_result.order_id,
            order_result.status,
        )
        return True

    async def pull_delivery_status(
        self, delivery_id: str, db: AsyncSession
    ) -> bool:
        """
        Nine United 포털에서 배송 상태를 조회하여 내부 DB 업데이트
        """
        result = await db.execute(
            select(Delivery).where(Delivery.id == delivery_id)
        )
        delivery = result.scalar_one_or_none()

        if delivery is None:
            logger.warning("배송 정보 없음: delivery_id=%s", delivery_id)
            return False

        status_result = await self.client.get_delivery_status(str(delivery.id))

        new_status = _STATUS_MAP.get(status_result.status)
        if new_status is not None and delivery.delivery_status != new_status:
            old_status = delivery.delivery_status
            delivery.delivery_status = new_status
            await db.flush()
            logger.info(
                "Nine United → DB 배송 상태 업데이트: delivery_id=%s, %s → %s",
                delivery_id,
                old_status,
                new_status,
            )
        else:
            logger.debug(
                "Nine United 배송 상태 변경 없음: delivery_id=%s, status=%s",
                delivery_id,
                status_result.status,
            )

        return True
