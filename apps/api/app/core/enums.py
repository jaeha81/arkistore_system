"""
전체 시스템 Enum 중앙 관리
모든 상태값/타입은 반드시 이 파일에서 정의하고 import한다
"""
from enum import Enum


# ==================== 운영 도메인 ====================

class ProjectStatus(str, Enum):
    active = "active"
    paused = "paused"
    archived = "archived"


class OperationMode(str, Enum):
    normal = "normal"
    manual_support = "manual_support"
    agent_enabled = "agent_enabled"
    hybrid = "hybrid"


class Environment(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"


class SiteType(str, Enum):
    main_dashboard = "main_dashboard"
    logistics = "logistics"
    sales = "sales"
    store_manager = "store_manager"


class IssueStatus(str, Enum):
    new = "new"
    grouped = "grouped"
    triaged = "triaged"
    github_created = "github_created"
    resolved = "resolved"
    ignored = "ignored"


# ==================== 업무 도메인 ====================

class InventoryStatus(str, Enum):
    normal = "normal"
    low_stock = "low_stock"
    out_of_stock = "out_of_stock"
    inbound_pending = "inbound_pending"


class CustomerGrade(str, Enum):
    normal = "normal"
    repeat = "repeat"
    vip = "vip"


class LeadStatus(str, Enum):
    new = "new"
    in_progress = "in_progress"
    converted = "converted"
    closed = "closed"
    dropped = "dropped"


class ContractStatus(str, Enum):
    draft = "draft"
    signed = "signed"
    confirmed = "confirmed"
    cancelled = "cancelled"


class PurchaseRequestStatus(str, Enum):
    requested = "requested"
    reviewed = "reviewed"
    approved = "approved"
    rejected = "rejected"
    converted_to_order = "converted_to_order"


class PurchaseOrderStatus(str, Enum):
    created = "created"
    ordered = "ordered"
    invoiced = "invoiced"
    shipped = "shipped"
    completed = "completed"
    cancelled = "cancelled"


class PaymentStatus(str, Enum):
    unpaid = "unpaid"
    partially_paid = "partially_paid"
    paid = "paid"


class DeliveryStatus(str, Enum):
    scheduled = "scheduled"
    confirmed = "confirmed"
    in_transit = "in_transit"
    completed = "completed"
    delayed = "delayed"
    cancelled = "cancelled"


class SlotStatus(str, Enum):
    open = "open"
    limited = "limited"
    full = "full"
    closed = "closed"


# ==================== 공통 ====================

class UserRole(str, Enum):
    super_admin = "super_admin"
    ops_admin = "ops_admin"
    arki_logistics = "arki_logistics"
    arki_sales = "arki_sales"
    arki_store_manager = "arki_store_manager"
    support_operator = "support_operator"


class SyncJobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
