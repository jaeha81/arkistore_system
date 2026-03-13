"""
외부 연동 어댑터 통합 모듈
Adapter-First + Mock-First 원칙
"""
from app.integrations.customs.adapter import CustomsAdapter
from app.integrations.customs.client import get_customs_client
from app.integrations.ecount.adapter import EcountAdapter
from app.integrations.ecount.client import get_ecount_client
from app.integrations.nine_united.adapter import NineUnitedAdapter
from app.integrations.nine_united.client import get_nine_united_client

__all__ = [
    "EcountAdapter",
    "get_ecount_client",
    "NineUnitedAdapter",
    "get_nine_united_client",
    "CustomsAdapter",
    "get_customs_client",
]
