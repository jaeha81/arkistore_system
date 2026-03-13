"""
Alembic autogenerate를 위한 모든 모델 import
이 파일은 절대 삭제하지 않는다
"""
from app.core.database import Base  # noqa: F401

# 운영 도메인 모델
from app.models.user import User  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.project_site import ProjectSite  # noqa: F401
from app.models.error_report import ErrorReport  # noqa: F401
from app.models.issue_group import IssueGroup  # noqa: F401
from app.models.github_issue import GithubIssue  # noqa: F401
from app.models.event_log import EventLog  # noqa: F401
from app.models.admin_action import AdminAction  # noqa: F401
from app.models.deployment_record import DeploymentRecord  # noqa: F401
from app.models.sheet_sync_job import SheetSyncJob  # noqa: F401

# 업무 도메인 모델
from app.models.product import Product  # noqa: F401
from app.models.inventory import Inventory  # noqa: F401
from app.models.customer import Customer  # noqa: F401
from app.models.lead import Lead  # noqa: F401
from app.models.consultation import Consultation  # noqa: F401
from app.models.contract import Contract  # noqa: F401
from app.models.purchase_request import PurchaseRequest, PurchaseRequestItem  # noqa: F401
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem  # noqa: F401
from app.models.invoice import Invoice  # noqa: F401
from app.models.shipment import Shipment  # noqa: F401
from app.models.delivery import Delivery  # noqa: F401
from app.models.capacity_slot import CapacitySlot  # noqa: F401
from app.models.happy_call import HappyCall  # noqa: F401
from app.models.attachment import Attachment  # noqa: F401
