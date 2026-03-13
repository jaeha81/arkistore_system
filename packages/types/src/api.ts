export interface ApiMeta {
  request_id: string | null;
  timestamp: string;
}

export interface PaginationMeta extends ApiMeta {
  page: number;
  page_size: number;
  total: number;
}

export interface ApiResponse<T> {
  success: true;
  data: T;
  meta: ApiMeta;
}

export interface PaginatedApiResponse<T> {
  success: true;
  data: T[];
  meta: PaginationMeta;
}

export interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details: unknown;
    trace_id: string | null;
  };
  meta: ApiMeta;
}
