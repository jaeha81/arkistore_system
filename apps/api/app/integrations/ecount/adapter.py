"""
Ecount ERP Adapter
서비스에서 직접 사용하는 인터페이스
Ecount ↔ 내부 DB 동기화 담당
"""
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.ecount.client import (
    BaseEcountClient,
    get_ecount_client,
)
from app.models.inventory import Inventory
from app.models.product import Product

logger = logging.getLogger(__name__)


class EcountAdapter:
    """Ecount ERP 연동 어댑터"""

    def __init__(self, client: BaseEcountClient | None = None):
        self.client = client or get_ecount_client()

    async def sync_product_from_ecount(
        self, product_code: str, db: AsyncSession
    ) -> Product:
        """
        Ecount에서 상품 정보를 가져와 products 테이블에 upsert
        """
        ecount_product = await self.client.get_product(product_code)

        result = await db.execute(
            select(Product).where(Product.product_code == product_code)
        )
        product = result.scalar_one_or_none()

        if product is None:
            product = Product(
                product_code=ecount_product.product_code,
                product_name=ecount_product.product_name,
                brand_name="",
                category_name=ecount_product.category_name,
                unit_price=ecount_product.unit_price,
                currency=ecount_product.currency,
                supplier_name=ecount_product.supplier_name,
                is_active=ecount_product.is_active,
            )
            db.add(product)
            logger.info("Ecount → DB 신규 상품 생성: %s", product_code)
        else:
            product.product_name = ecount_product.product_name
            product.category_name = ecount_product.category_name
            product.unit_price = ecount_product.unit_price
            product.currency = ecount_product.currency
            product.supplier_name = ecount_product.supplier_name
            product.is_active = ecount_product.is_active
            logger.info("Ecount → DB 상품 업데이트: %s", product_code)

        await db.flush()
        return product

    async def sync_inventory_to_ecount(
        self, product_id: str, db: AsyncSession
    ) -> bool:
        """
        내부 재고 정보를 Ecount로 push
        """
        result = await db.execute(
            select(Inventory)
            .join(Product, Inventory.product_id == Product.id)
            .where(Product.id == product_id)
        )
        inventory = result.scalar_one_or_none()

        if inventory is None:
            logger.warning("재고 정보 없음: product_id=%s", product_id)
            return False

        product_result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = product_result.scalar_one_or_none()

        if product is None:
            logger.warning("상품 정보 없음: product_id=%s", product_id)
            return False

        sync_result = await self.client.sync_inventory(
            product_code=product.product_code,
            quantity=float(inventory.current_stock),
        )

        logger.info(
            "DB → Ecount 재고 동기화: %s, 수량=%s, 성공=%s",
            product.product_code,
            sync_result.synced_quantity,
            sync_result.sync_success,
        )
        return sync_result.sync_success
