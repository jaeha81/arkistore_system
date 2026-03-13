"""
Repository 패키지
모든 DB 접근 로직을 여기서 관리한다
"""
from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.base import BaseRepository
from app.repositories.capacity_slot_repository import CapacitySlotRepository
from app.repositories.consultation_repository import ConsultationRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.event_log_repository import EventLogRepository
from app.repositories.happy_call_repository import HappyCallRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.issue_repository import IssueRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.repositories.purchase_request_repository import PurchaseRequestRepository
from app.repositories.shipment_repository import ShipmentRepository
from app.repositories.sync_job_repository import SyncJobRepository
from app.repositories.user_repository import UserRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "ProjectRepository",
    "ProductRepository",
    "InventoryRepository",
    "CustomerRepository",
    "LeadRepository",
    "ConsultationRepository",
    "ContractRepository",
    "PurchaseRequestRepository",
    "PurchaseOrderRepository",
    "InvoiceRepository",
    "ShipmentRepository",
    "DeliveryRepository",
    "CapacitySlotRepository",
    "HappyCallRepository",
    "AttachmentRepository",
    "EventLogRepository",
    "IssueRepository",
    "SyncJobRepository",
]
