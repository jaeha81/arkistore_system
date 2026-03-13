"""
상품 스키마
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    brand_name: str
    product_code: str
    product_name: str
    category_name: str | None = None
    option_text: str | None = None
    unit_price: Decimal
    currency: str = "USD"
    supplier_name: str | None = None
    is_active: bool = True


class ProductUpdate(BaseModel):
    brand_name: str | None = None
    product_name: str | None = None
    category_name: str | None = None
    option_text: str | None = None
    unit_price: Decimal | None = None
    currency: str | None = None
    supplier_name: str | None = None
    is_active: bool | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    brand_name: str
    product_code: str
    product_name: str
    category_name: str | None = None
    option_text: str | None = None
    unit_price: Decimal
    currency: str
    supplier_name: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
