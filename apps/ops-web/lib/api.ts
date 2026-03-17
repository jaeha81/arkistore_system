/**
 * ops-web API 클라이언트
 * 백엔드 /api/v1/* 호출
 */
import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // httpOnly cookie 전송
  headers: {
    "Content-Type": "application/json",
  },
});

// 응답 인터셉터: 401이면 로그인 페이지로
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // TODO: 로그인 활성화 시 아래 주석 해제
    // if (error.response?.status === 401) {
    //   window.location.href = "/login";
    // }
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

// ==================== Ops Projects ====================
export const projectsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/ops/projects", { params }),
  get: (id: string) => apiClient.get(`/ops/projects/${id}`),
  create: (data: unknown) => apiClient.post("/ops/projects", data),
  update: (id: string, data: unknown) => apiClient.patch(`/ops/projects/${id}`, data),
  delete: (id: string) => apiClient.delete(`/ops/projects/${id}`),
  listSites: (projectId: string) => apiClient.get(`/ops/projects/${projectId}/sites`),
  createSite: (projectId: string, data: unknown) =>
    apiClient.post(`/ops/projects/${projectId}/sites`, data),
};

// ==================== Ops Issues ====================
export const issuesApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/ops/issues", { params }),
  get: (id: string) => apiClient.get(`/ops/issues/${id}`),
  updateStatus: (id: string, data: unknown) =>
    apiClient.patch(`/ops/issues/${id}/status`, data),
  listGroups: (params?: Record<string, unknown>) =>
    apiClient.get("/ops/issue-groups", { params }),
  getGroup: (id: string) => apiClient.get(`/ops/issue-groups/${id}`),
  updateGroupStatus: (id: string, data: unknown) =>
    apiClient.patch(`/ops/issue-groups/${id}/status`, data),
  listByGroup: (groupId: string) =>
    apiClient.get("/ops/issues", { params: { group_id: groupId } }),
  createGithubIssue: (groupId: string, data: unknown, idempotencyKey: string) =>
    apiClient.post(`/ops/issue-groups/${groupId}/github-issue`, data, {
      headers: { "Idempotency-Key": idempotencyKey },
    }),
};

// ==================== Ops Logs ====================
export const logsApi = {
  listEvents: (params?: Record<string, unknown>) =>
    apiClient.get("/ops/logs/events", { params }),
  getEvent: (id: string) => apiClient.get(`/ops/logs/events/${id}`),
  listErrors: (params?: Record<string, unknown>) =>
    apiClient.get("/ops/logs/errors", { params }),
  getError: (id: string) => apiClient.get(`/ops/logs/errors/${id}`),
};
