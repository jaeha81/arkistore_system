"""
UNI-PASS 통관조회 Adapter
서비스에서 직접 사용하는 인터페이스
UNI-PASS ↔ 내부 DB 동기화 담당
"""
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.customs.client import (
    BaseCustomsClient,
    get_customs_client,
)
from app.models.shipment import Shipment

logger = logging.getLogger(__name__)


class CustomsAdapter:
    """UNI-PASS 통관조회 연동 어댑터"""

    def __init__(self, client: BaseCustomsClient | None = None):
        self.client = client or get_customs_client()

    async def update_shipment_customs_status(
        self, shipment_id: str, db: AsyncSession
    ) -> bool:
        """
        UNI-PASS에서 통관 상태를 조회하여 shipment.customs_status 업데이트
        """
        result = await db.execute(
            select(Shipment).where(Shipment.id == shipment_id)
        )
        shipment = result.scalar_one_or_none()

        if shipment is None:
            logger.warning("선적 정보 없음: shipment_id=%s", shipment_id)
            return False

        customs_result = await self.client.get_customs_status(shipment.bl_number)

        old_status = shipment.customs_status
        new_status = customs_result.customs_status

        if old_status != new_status:
            shipment.customs_status = new_status
            await db.flush()
            logger.info(
                "UNI-PASS → DB 통관 상태 업데이트: shipment_id=%s, bl=%s, %s → %s",
                shipment_id,
                shipment.bl_number,
                old_status,
                new_status,
            )
        else:
            logger.debug(
                "UNI-PASS 통관 상태 변경 없음: shipment_id=%s, status=%s",
                shipment_id,
                old_status,
            )

        return True
