/**
 * arki-web API 클라이언트
 * 백엔드 /api/v1/arki/* 호출
 */
import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ==================== Auth ====================
export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post("/auth/login", { email, password }),
  logout: () => apiClient.post("/auth/logout"),
  me: () => apiClient.get("/auth/me"),
};

// ==================== Dashboard ====================
export const dashboardApi = {
  summary: () => apiClient.get("/arki/dashboard/summary"),
  deliveryTrend: (days = 7) =>
    apiClient.get("/arki/dashboard/delivery-trend", { params: { days } }),
};

// ==================== Products ====================
export const productsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/arki/products", { params }),
  get: (id: string) => apiClient.get(`/arki/products/${id}`),
  create: (data: unknown) => apiClient.post("/arki/products", data),
  update: (id: string, data: unknown) => apiClient.patch(`/arki/products/${id}`, data),
};

// ==================== Inventory ====================
export const inventoryApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/arki/inventory", { params }),
  get: (id: string) => apiClient.get(`/arki/inventory/${id}`),
  update: (id: string, data: unknown) => apiClient.patch(`/arki/inventory/${id}`, data),
};

// ==================== Customers ====================
export const customersApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/arki/customers", { params }),
  get: (id: string) => apiClient.get(`/arki/customers/${id}`),
  create: (data: unknown) => apiClient.post("/arki/customers", data),
  update: (id: string, data: unknown) => apiClient.patch(`/arki/customers/${id}`, data),
};

// ==================== Leads ====================
export const leadsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/arki/leads", { params }),
  get: (id: string) => apiClient.get(`/arki/leads/${id}`),
  create: (data: unknown) => apiClient.post("/arki/leads", data),
  update: (id: string, data: unknown) => apiClient.patch(`/arki/leads/${id}`, data),
};

// ==================== Consultations ====================
export const consultationsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/arki/consultations", { params }),
  get: (id: string) => apiClient.get(`/arki/consultations/${id}`),
  create: (data: unknown) => apiClient.post("/arki/consultations", data),
  update: (id: string, data: unknown) => apiClient.patch(`/arki/consultations/${id}`, data),
};

// ==================== Contracts ====================
export const contractsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/arki/contracts", { params }),
  get: (id: string) => apiClient.get(`/arki/contracts/${id}`),
  create: (data: unknown, idempotencyKey: string) =>
    apiClient.post("/arki/contracts", data, {
      headers: { "Idempotency-Key": idempotencyKey },
    }),
  update: (id: string, data: unknown) =>
    apiClient.patch(`/arki/contracts/${id}`, data),
  attachFile: (contractId: string, data: unknown) =>
    apiClient.post(`/arki/contracts/${contractId}/attachments`, data),
  listAttachments: (contractId: string) =>
    apiClient.get(`/arki/contracts/${contractId}/attachments`),
};

// ==================== Purchase Requests ====================
export const purchaseRequestsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/arki/purchase-requests", { params }),
  get: (id: string) => apiClient.get(`/arki/purchase-requests/${id}`),
  create: (data: unknown, idempotencyKey: string) =>
    apiClient.post("/arki/purchase-requests", data, {
      headers: { "Idempotency-Key": idempotencyKey },
    }),
  update: (id: string, data: unknown) =>
    apiClient.patch(`/arki/purchase-requests/${id}`, data),
};

// ==================== Purchase Orders ====================
export const purchaseOrdersApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/arki/purchase-orders", { params }),
  get: (id: string) => apiClient.get(`/arki/purchase-orders/${id}`),
  create: (data: unknown, idempotencyKey: string) =>
    apiClient.post("/arki/purchase-orders", data, {
      headers: { "Idempotency-Key": idempotencyKey },
    }),
  update: (id: string, data: unknown) =>
    apiClient.patch(`/arki/purchase-orders/${id}`, data),
};

// ==================== Invoices ====================
export const invoicesApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/arki/invoices", { params }),
  get: (id: string) => apiClient.get(`/arki/invoices/${id}`),
  create: (data: unknown) => apiClient.post("/arki/invoices", data),
  update: (id: string, data: unknown) => apiClient.patch(`/arki/invoices/${id}`, data),
};

// ==================== Shipments ====================
export const shipmentsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/arki/shipments", { params }),
  get: (id: string) => apiClient.get(`/arki/shipments/${id}`),
  create: (data: unknown) => apiClient.post("/arki/shipments", data),
  update: (id: string, data: unknown) => apiClient.patch(`/arki/shipments/${id}`, data),
};

// ==================== Deliveries ====================
export const deliveriesApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/arki/deliveries", { params }),
  get: (id: string) => apiClient.get(`/arki/deliveries/${id}`),
  create: (data: unknown, idempotencyKey: string) =>
    apiClient.post("/arki/deliveries", data, {
      headers: { "Idempotency-Key": idempotencyKey },
    }),
  update: (id: string, data: unknown) =>
    apiClient.patch(`/arki/deliveries/${id}`, data),
};

// ==================== Capacity Slots ====================
export const capacitySlotsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/arki/capacity-slots", { params }),
  create: (data: unknown) => apiClient.post("/arki/capacity-slots", data),
  update: (id: string, data: unknown) =>
    apiClient.patch(`/arki/capacity-slots/${id}`, data),
};

// ==================== Happy Calls ====================
export const happyCallsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/arki/happy-calls", { params }),
  get: (id: string) => apiClient.get(`/arki/happy-calls/${id}`),
  create: (data: unknown) => apiClient.post("/arki/happy-calls", data),
  update: (id: string, data: unknown) => apiClient.patch(`/arki/happy-calls/${id}`, data),
};

// ==================== Files ====================
export const filesApi = {
  presign: (data: { file_name: string; file_type: string; related_table: string }) =>
    apiClient.post("/files/presign", data),
};
