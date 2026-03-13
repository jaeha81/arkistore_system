"""
Pydantic v2 스키마 패키지
모든 Request/Response 스키마를 여기서 관리한다
"""
from app.schemas.auth import LoginRequest, MeResponse, TokenResponse, UserSummary
from app.schemas.capacity_slot import CapacitySlotCreate, CapacitySlotRead, CapacitySlotUpdate
from app.schemas.common import (
    ErrorResponse,
    MetaSchema,
    PaginatedResponse,
    PaginationMetaSchema,
    SuccessResponse,
)
from app.schemas.consultation import ConsultationCreate, ConsultationRead
from app.schemas.contract import ContractAttachmentRequest, ContractCreate, ContractRead, ContractUpdate
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.schemas.dashboard import DashboardSummary
from app.schemas.delivery import DeliveryCreate, DeliveryRead, DeliveryUpdate
from app.schemas.error_report import ErrorReportCreate, ErrorReportCreateResponse
from app.schemas.file import FilePresignRequest, FilePresignResponse
from app.schemas.happy_call import HappyCallCreate, HappyCallRead
from app.schemas.inventory import InventoryRead, InventoryUpdate
from app.schemas.invoice import InvoiceCreate, InvoiceRead
from app.schemas.issue import (
    GithubIssueCreate,
    GithubIssueCreateResponse,
    IssueGroupRead,
    IssueStatusUpdate,
    IssueSummary,
)
from app.schemas.lead import LeadCreate, LeadRead, LeadUpdate
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.schemas.project import (
    ProjectCreate,
    ProjectRead,
    ProjectSiteCreate,
    ProjectSiteRead,
    ProjectUpdate,
)
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderItemInput,
    PurchaseOrderRead,
    PurchaseOrderUpdate,
)
from app.schemas.purchase_request import (
    PurchaseRequestCreate,
    PurchaseRequestItemInput,
    PurchaseRequestRead,
    PurchaseRequestUpdate,
)
from app.schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate
from app.schemas.sync import SheetExportRequest, SheetSyncJobRead

__all__ = [
    # common
    "MetaSchema",
    "PaginationMetaSchema",
    "SuccessResponse",
    "PaginatedResponse",
    "ErrorResponse",
    # auth
    "LoginRequest",
    "UserSummary",
    "TokenResponse",
    "MeResponse",
    # project
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectRead",
    "ProjectSiteCreate",
    "ProjectSiteRead",
    # product
    "ProductCreate",
    "ProductUpdate",
    "ProductRead",
    # inventory
    "InventoryUpdate",
    "InventoryRead",
    # customer
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerRead",
    # lead
    "LeadCreate",
    "LeadUpdate",
    "LeadRead",
    # consultation
    "ConsultationCreate",
    "ConsultationRead",
    # contract
    "ContractCreate",
    "ContractUpdate",
    "ContractRead",
    "ContractAttachmentRequest",
    # purchase_request
    "PurchaseRequestItemInput",
    "PurchaseRequestCreate",
    "PurchaseRequestUpdate",
    "PurchaseRequestRead",
    # purchase_order
    "PurchaseOrderItemInput",
    "PurchaseOrderCreate",
    "PurchaseOrderUpdate",
    "PurchaseOrderRead",
    # invoice
    "InvoiceCreate",
    "InvoiceRead",
    # shipment
    "ShipmentCreate",
    "ShipmentUpdate",
    "ShipmentRead",
    # delivery
    "DeliveryCreate",
    "DeliveryUpdate",
    "DeliveryRead",
    # capacity_slot
    "CapacitySlotCreate",
    "CapacitySlotUpdate",
    "CapacitySlotRead",
    # happy_call
    "HappyCallCreate",
    "HappyCallRead",
    # issue
    "IssueSummary",
    "IssueStatusUpdate",
    "IssueGroupRead",
    "GithubIssueCreate",
    "GithubIssueCreateResponse",
    # dashboard
    "DashboardSummary",
    # file
    "FilePresignRequest",
    "FilePresignResponse",
    # sync
    "SheetExportRequest",
    "SheetSyncJobRead",
    # error_report
    "ErrorReportCreate",
    "ErrorReportCreateResponse",
]
