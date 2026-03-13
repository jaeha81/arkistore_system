/**
 * Arkistore 공유 타입 정의
 * 백엔드 OpenAPI 스키마와 동기화 유지
 */

// ==================== 공통 ====================
export interface Meta {
  request_id: string | null;
  timestamp: string;
  page?: number;
  page_size?: number;
  total?: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  meta: Meta;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  meta: Meta & { page: number; page_size: number; total: number };
}

export interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details: unknown;
    trace_id: string | null;
  };
  meta: Meta;
}

// ==================== Enums ====================
export type ProjectStatus = "active" | "paused" | "archived";
export type OperationMode = "normal" | "manual_support" | "agent_enabled" | "hybrid";
export type InventoryStatus = "normal" | "low_stock" | "out_of_stock" | "inbound_pending";
export type CustomerGrade = "normal" | "repeat" | "vip";
export type LeadStatus = "new" | "in_progress" | "converted" | "closed" | "dropped";
export type ContractStatus = "draft" | "signed" | "confirmed" | "cancelled";
export type PurchaseRequestStatus =
  | "requested"
  | "reviewed"
  | "approved"
  | "rejected"
  | "converted_to_order";
export type PurchaseOrderStatus =
  | "created"
  | "ordered"
  | "invoiced"
  | "shipped"
  | "completed"
  | "cancelled";
export type PaymentStatus = "unpaid" | "partially_paid" | "paid";
export type DeliveryStatus =
  | "scheduled"
  | "confirmed"
  | "in_transit"
  | "completed"
  | "delayed"
  | "cancelled";
export type SlotStatus = "open" | "limited" | "full" | "closed";

// ==================== Dashboard ====================
export interface DashboardSummary {
  orders_total: number;
  purchase_requests_pending: number;
  low_stock_count: number;
  new_inquiries_count: number;
  deliveries_today: number;
  capa_remaining_today: number;
  open_issue_count: number;
}

// ==================== Products ====================
export interface Product {
  id: string;
  brand_name: string;
  product_code: string;
  product_name: string;
  category_name: string | null;
  option_text: string | null;
  unit_price: number;
  currency: string;
  supplier_name: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ==================== Customer ====================
export interface Customer {
  id: string;
  customer_type: string;
  name: string;
  phone_masked: string | null;
  email_masked: string | null;
  region: string | null;
  source_channel: string | null;
  grade: CustomerGrade;
  is_vip: boolean;
  created_at: string;
}

// ==================== Contract ====================
export interface Contract {
  id: string;
  contract_number: string | null;
  customer_id: string;
  consultation_id: string | null;
  contract_date: string;
  contract_amount: number;
  deposit_amount: number | null;
  contract_status: ContractStatus;
  delivery_required: boolean;
  remarks: string | null;
  created_at: string;
  updated_at: string;
}

// ==================== Delivery ====================
export interface Delivery {
  id: string;
  delivery_number: string | null;
  contract_id: string;
  customer_id: string;
  delivery_date: string;
  time_slot: string;
  delivery_team: string;
  vehicle_code: string | null;
  address_text: string;
  ladder_required: boolean;
  delivery_status: DeliveryStatus;
  created_at: string;
}

// ==================== Capacity Slot ====================
export interface CapacitySlot {
  id: string;
  slot_date: string;
  delivery_team: string;
  time_slot: string;
  max_capacity: number;
  used_capacity: number;
  remaining_capacity: number;
  slot_status: SlotStatus;
}
