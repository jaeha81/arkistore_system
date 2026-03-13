# 05 API CONTRACT — Arkistore Operations Automation System

전체 API 엔드포인트 계약 명세. 인증, 권한, 요청/응답 구조, 에러 코드를 정의한다.

---

## 공통 규칙

### 인증
- 모든 보호 엔드포인트: `Authorization: Bearer <JWT>` 또는 httpOnly 쿠키 `access_token`
- JWT 만료: 1시간 (access), 7일 (refresh)

### 공통 응답 구조
```json
{
  "data": { ... },
  "meta": { "total": 100, "page": 1, "limit": 20 }
}
```

### 공통 에러 응답
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "설명",
    "details": [ ... ]
  }
}
```

### 공통 에러 코드
| 코드 | HTTP | 설명 |
|------|------|------|
| UNAUTHORIZED | 401 | 인증 토큰 없음 또는 만료 |
| FORBIDDEN | 403 | 권한 없음 |
| NOT_FOUND | 404 | 리소스 없음 |
| VALIDATION_ERROR | 422 | 요청 데이터 유효성 오류 |
| CONFLICT | 409 | 중복 키 충돌 (Idempotency-Key 포함) |
| INTERNAL_ERROR | 500 | 서버 내부 오류 |

### Idempotency-Key
- 헤더: `Idempotency-Key: <UUID v4>`
- 동일 키로 재요청 시 최초 응답 그대로 반환 (멱등성 보장)
- 유효 기간: 24시간

---

## 1. Auth - 인증

### POST /api/v1/auth/login
- **인증**: 불필요
- **권한**: 없음
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| email | string | ✅ | 사용자 이메일 |
| password | string | ✅ | 비밀번호 (평문, TLS 전송) |

- **Response 200**:
```json
{
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "홍길동",
      "role": "arki_logistics"
    }
  }
}
```
- **Error Codes**:
  - `INVALID_CREDENTIALS` (401): 이메일 또는 비밀번호 불일치
  - `ACCOUNT_INACTIVE` (403): 비활성 계정

---

### POST /api/v1/auth/logout
- **인증**: 필요
- **권한**: 로그인된 모든 역할
- **Request Body**: 없음
- **Response 200**:
```json
{ "data": { "message": "로그아웃 완료" } }
```

---

### GET /api/v1/auth/me
- **인증**: 필요
- **권한**: 로그인된 모든 역할
- **Response 200**:
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "홍길동",
    "role": "arki_logistics",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

---

## 2. Ops - Projects (프로젝트 관리)

### GET /api/v1/ops/projects
- **인증**: 필요
- **권한**: super_admin, ops_admin, support_operator
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| status | string | ❌ | active, maintenance, inactive, archived (콤마 구분 복수 가능) |
| operation_mode | string | ❌ | normal, readonly, emergency |
| q | string | ❌ | 프로젝트명, 클라이언트명, project_code 검색 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20, 최대 100 |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "project_code": "ARKI",
      "name": "Arkistore",
      "client_name": "아키스토어",
      "service_type": "ecommerce",
      "main_url": "https://arkistore.com",
      "status": "active",
      "operation_mode": "normal",
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z"
    }
  ],
  "meta": { "total": 5, "page": 1, "limit": 20 }
}
```

---

### POST /api/v1/ops/projects
- **인증**: 필요
- **권한**: super_admin, ops_admin
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| project_code | string | ✅ | 고유 코드 (영문 대문자, 최대 50자) |
| name | string | ✅ | 프로젝트명 |
| client_name | string | ✅ | 클라이언트명 |
| service_type | string | ✅ | 서비스 유형 |
| main_url | string | ❌ | 메인 URL |
| status | string | ❌ | 기본값 active |
| operation_mode | string | ❌ | 기본값 normal |

- **Response 201**: 생성된 프로젝트 객체 (GET 단건 응답과 동일)
- **Error Codes**:
  - `DUPLICATE_PROJECT_CODE` (409): project_code 중복

---

### GET /api/v1/ops/projects/{id}
- **인증**: 필요
- **권한**: super_admin, ops_admin, support_operator
- **Response 200**: 프로젝트 단건 객체 (sites 배열 포함)

---

### PATCH /api/v1/ops/projects/{id}
- **인증**: 필요
- **권한**: super_admin, ops_admin
- **Request Body** (부분 업데이트):

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| name | string | ❌ | 프로젝트명 |
| client_name | string | ❌ | 클라이언트명 |
| service_type | string | ❌ | 서비스 유형 |
| main_url | string | ❌ | 메인 URL |
| status | string | ❌ | 상태 변경 |
| operation_mode | string | ❌ | 운영 모드 변경 |

- **Response 200**: 업데이트된 프로젝트 객체

---

### GET /api/v1/ops/projects/{id}/sites
- **인증**: 필요
- **권한**: super_admin, ops_admin, support_operator
- **Response 200**: 사이트 목록 배열

---

### POST /api/v1/ops/projects/{id}/sites
- **인증**: 필요
- **권한**: super_admin, ops_admin
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| site_code | string | ✅ | 고유 사이트 코드 |
| site_name | string | ✅ | 사이트명 |
| site_url | string | ❌ | 사이트 URL |
| site_type | string | ✅ | SiteType enum |
| is_enabled | boolean | ❌ | 기본값 true |

- **Response 201**: 생성된 사이트 객체

---

### PATCH /api/v1/ops/projects/{id}/sites/{site_id}
- **인증**: 필요
- **권한**: super_admin, ops_admin
- **Request Body**: site_name, site_url, site_type, is_enabled (부분 업데이트)
- **Response 200**: 업데이트된 사이트 객체

---

## 3. Ops - Issues (이슈 그룹 관리)

### GET /api/v1/ops/issues
- **인증**: 필요
- **권한**: super_admin, ops_admin, support_operator
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| status | string | ❌ | new, grouped, triaged, github_created, resolved, ignored (콤마 구분) |
| project_code | string | ❌ | 프로젝트 코드 필터 |
| q | string | ❌ | group_title, error_code 검색 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20 |
| sort | string | ❌ | last_seen_at:desc (기본값), occurrence_count:desc |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "group_key": "ARKI-E001-LoginScreen",
      "group_title": "로그인 화면 인증 오류",
      "occurrence_count": 42,
      "first_seen_at": "2026-01-01T00:00:00Z",
      "last_seen_at": "2026-03-10T12:00:00Z",
      "group_status": "triaged",
      "github_issue_id": null,
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-03-10T12:00:00Z"
    }
  ],
  "meta": { "total": 15, "page": 1, "limit": 20 }
}
```

---

### PATCH /api/v1/ops/issues/{group_id}/status
- **인증**: 필요
- **권한**: super_admin, ops_admin, support_operator
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| status | string | ✅ | 변경할 상태 (IssueStatus enum) |
| notes | string | ❌ | 상태 변경 사유 |

- **Response 200**: 업데이트된 이슈 그룹 객체
- **Error Codes**:
  - `INVALID_STATUS_TRANSITION` (422): 허용되지 않는 상태 전이

---

### POST /api/v1/ops/issues/{group_id}/github
- **인증**: 필요
- **권한**: super_admin, ops_admin, support_operator
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| repository | string | ✅ | GitHub 저장소 (owner/repo 형식) |
| title | string | ❌ | 이슈 제목 (미입력 시 group_title 사용) |
| body | string | ❌ | 이슈 본문 (미입력 시 자동 생성) |
| labels | array[string] | ❌ | GitHub 라벨 목록 |

- **Response 201**:
```json
{
  "data": {
    "id": "uuid",
    "issue_group_id": "uuid",
    "repository": "owner/repo",
    "github_issue_number": 123,
    "github_issue_url": "https://github.com/owner/repo/issues/123",
    "state": "open",
    "created_by": "uuid",
    "created_at": "2026-03-12T00:00:00Z"
  }
}
```
- **Error Codes**:
  - `GITHUB_ISSUE_ALREADY_EXISTS` (409): 해당 그룹에 이미 GitHub 이슈 존재
  - `GITHUB_API_ERROR` (502): GitHub API 연동 오류

---

## 4. Ops - Logs (로그 관리)

### GET /api/v1/ops/logs/events
- **인증**: 필요
- **권한**: super_admin, ops_admin, support_operator
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| project_code | string | ❌ | 프로젝트 코드 필터 |
| environment | string | ❌ | production, staging, development |
| event_type | string | ❌ | 이벤트 타입 필터 |
| from_date | string | ❌ | ISO 8601 날짜 (logged_at 기준) |
| to_date | string | ❌ | ISO 8601 날짜 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 50, 최대 200 |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "project_code": "ARKI",
      "environment": "production",
      "app_version": "1.2.3",
      "event_type": "user_action",
      "event_name": "contract_created",
      "payload": { "contract_id": "uuid" },
      "logged_at": "2026-03-12T10:00:00Z"
    }
  ],
  "meta": { "total": 500, "page": 1, "limit": 50 }
}
```

---

### GET /api/v1/ops/error-reports
- **인증**: 필요
- **권한**: super_admin, ops_admin, support_operator
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| project_code | string | ❌ | 프로젝트 코드 필터 |
| site_type | string | ❌ | SiteType enum |
| environment | string | ❌ | production, staging, development |
| report_status | string | ❌ | new, grouped, triaged, github_created, resolved, ignored |
| from_date | string | ❌ | ISO 8601 (occurred_at 기준) |
| to_date | string | ❌ | ISO 8601 |
| project_id | string | ❌ | 프로젝트 UUID 필터 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 50 |
| sort | string | ❌ | occurred_at:desc (기본값) |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "project_code": "ARKI",
      "site_type": "arki_web",
      "environment": "production",
      "app_version": "1.2.3",
      "screen_name": "LoginScreen",
      "error_code": "AUTH_001",
      "error_message_masked": "인증 오류: [MASKED]",
      "report_status": "new",
      "issue_group_id": null,
      "trace_id": "trace-abc123",
      "occurred_at": "2026-03-12T10:00:00Z",
      "created_at": "2026-03-12T10:00:01Z"
    }
  ],
  "meta": { "total": 200, "page": 1, "limit": 50 }
}
```

---

### POST /api/v1/ops/error-reports
- **인증**: 필요
- **권한**: super_admin, ops_admin, arki_logistics, arki_sales, arki_store_manager, support_operator
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| project_code | string | ✅ | 프로젝트 코드 |
| site_type | string | ✅ | SiteType enum |
| environment | string | ✅ | production, staging, development |
| app_version | string | ✅ | 앱 버전 |
| screen_name | string | ❌ | 화면명 |
| error_code | string | ✅ | 오류 코드 |
| error_message | string | ✅ | 원본 오류 메시지 |
| user_context | object | ❌ | 사용자 컨텍스트 JSONB |
| trace_id | string | ❌ | 트레이스 ID |
| occurred_at | string | ✅ | ISO 8601 발생 일시 |

- **Response 201**: 생성된 error_report 객체 (issue_group_id 자동 연결 포함)

---

## 5. Arki - Dashboard (대시보드)

### GET /api/v1/arki/dashboard/summary
- **인증**: 필요
- **권한**: super_admin, arki_logistics, arki_sales, arki_store_manager
- **Query Params**: 없음
- **Response 200**:
```json
{
  "data": {
    "pending_purchase_requests": 5,
    "low_stock_products": 3,
    "new_leads": 12,
    "today_deliveries": 8,
    "capa_remaining_rate": 0.65,
    "unresolved_error_reports": 2,
    "recent_actions": [
      {
        "action_type": "contract_created",
        "target_table": "contracts",
        "target_id": "uuid",
        "actor_name": "홍길동",
        "created_at": "2026-03-12T09:00:00Z"
      }
    ]
  }
}
```

---

## 6. Arki - Products (상품)

### GET /api/v1/arki/products
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| is_active | boolean | ❌ | 활성 여부 필터 |
| brand_name | string | ❌ | 브랜드명 필터 |
| category_name | string | ❌ | 카테고리 필터 |
| q | string | ❌ | product_code, product_name, supplier_name 검색 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20 |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "brand_name": "ARKI",
      "product_code": "PRD-001",
      "product_name": "소파 A형",
      "category_name": "소파",
      "option_text": "3인용/그레이",
      "unit_price": "1500000.0000",
      "currency": "KRW",
      "supplier_name": "공급사A",
      "is_active": true,
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z"
    }
  ],
  "meta": { "total": 50, "page": 1, "limit": 20 }
}
```

---

### POST /api/v1/arki/products
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| brand_name | string | ✅ | 브랜드명 |
| product_code | string | ✅ | 상품 코드 (UNIQUE) |
| product_name | string | ✅ | 상품명 |
| category_name | string | ❌ | 카테고리명 |
| option_text | string | ❌ | 옵션 텍스트 |
| unit_price | number | ✅ | 단가 |
| currency | string | ❌ | 통화 코드 (기본값 USD) |
| supplier_name | string | ❌ | 공급사명 |
| is_active | boolean | ❌ | 기본값 true |

- **Response 201**: 생성된 상품 객체
- **Error Codes**:
  - `DUPLICATE_PRODUCT_CODE` (409): product_code 중복

---

### PATCH /api/v1/arki/products/{id}
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Request Body**: 부분 업데이트 (brand_name, product_name, category_name, option_text, unit_price, currency, supplier_name, is_active)
- **Response 200**: 업데이트된 상품 객체

---

## 7. Arki - Inventory (재고)

### GET /api/v1/arki/inventory
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| inventory_status | string | ❌ | normal, low_stock, out_of_stock, overstock |
| warehouse_name | string | ❌ | 창고명 필터 |
| q | string | ❌ | product_code, product_name 검색 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20 |
| sort | string | ❌ | available_stock:asc (기본값) |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "product_id": "uuid",
      "product_code": "PRD-001",
      "product_name": "소파 A형",
      "warehouse_name": "인천창고",
      "current_stock": "100.0000",
      "reserved_stock": "20.0000",
      "available_stock": "80.0000",
      "safety_stock": "10.0000",
      "expected_inbound_date": "2026-04-01",
      "inventory_status": "normal",
      "updated_at": "2026-03-12T00:00:00Z"
    }
  ],
  "meta": { "total": 50, "page": 1, "limit": 20 }
}
```

---

### PATCH /api/v1/arki/inventory/{id}
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| current_stock | number | ❌ | 현재 재고 수동 조정 |
| safety_stock | number | ❌ | 안전 재고 기준 변경 |
| expected_inbound_date | string | ❌ | 입고 예정일 (YYYY-MM-DD) |
| warehouse_name | string | ❌ | 창고명 변경 |
| adjustment_reason | string | ✅ | 조정 사유 (admin_actions 기록용) |

- **Response 200**: 업데이트된 재고 객체

---

## 8. Arki - Customers (고객)

### GET /api/v1/arki/customers
- **인증**: 필요
- **권한**: super_admin, arki_sales, arki_store_manager
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| customer_type | string | ❌ | individual, business |
| grade | string | ❌ | CustomerGrade enum |
| is_vip | boolean | ❌ | VIP 여부 필터 |
| q | string | ❌ | name, phone_masked, email_masked 검색 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20 |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "customer_type": "individual",
      "name": "김철수",
      "phone_masked": "010-****-5678",
      "email_masked": "kim***@example.com",
      "region": "서울",
      "source_channel": "온라인",
      "grade": "gold",
      "is_vip": false,
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z"
    }
  ],
  "meta": { "total": 200, "page": 1, "limit": 20 }
}
```

---

### POST /api/v1/arki/customers
- **인증**: 필요
- **권한**: super_admin, arki_sales, arki_store_manager
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| customer_type | string | ✅ | individual, business |
| name | string | ✅ | 고객명 |
| phone | string | ❌ | 전화번호 (암호화 저장) |
| email | string | ❌ | 이메일 (암호화 저장) |
| region | string | ❌ | 지역 |
| source_channel | string | ❌ | 유입 채널 |
| grade | string | ❌ | CustomerGrade (기본값 normal) |
| is_vip | boolean | ❌ | VIP 여부 (arki_sales, super_admin만 true 설정 가능) |

- **Response 201**: 생성된 고객 객체 (phone_masked, email_masked 반환)

---

### PATCH /api/v1/arki/customers/{id}
- **인증**: 필요
- **권한**: super_admin, arki_sales, arki_store_manager
- **Request Body**: 부분 업데이트 (name, phone, email, region, source_channel, grade, is_vip)
- **비고**: is_vip 변경은 super_admin, arki_sales만 가능 (서버에서 역할 검증)
- **Response 200**: 업데이트된 고객 객체

---

## 9. Arki - Leads (리드)

### GET /api/v1/arki/leads
- **인증**: 필요
- **권한**: super_admin, arki_sales
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| status | string | ❌ | new, in_progress, converted, closed, dropped |
| source_channel | string | ❌ | 유입 채널 필터 |
| customer_id | string | ❌ | 고객 UUID 필터 |
| from_date | string | ❌ | ISO 8601 (created_at 기준) |
| to_date | string | ❌ | ISO 8601 |
| q | string | ❌ | 고객명, 연락처 검색 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20 |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "customer_id": "uuid",
      "customer_name": "김철수",
      "customer_phone_masked": "010-****-5678",
      "source_channel": "온라인",
      "interest_product": "소파 A형",
      "lead_status": "new",
      "memo": "3인용 소파 문의",
      "created_at": "2026-03-01T00:00:00Z",
      "updated_at": "2026-03-01T00:00:00Z"
    }
  ],
  "meta": { "total": 30, "page": 1, "limit": 20 }
}
```

---

### POST /api/v1/arki/leads
- **인증**: 필요
- **권한**: super_admin, arki_sales
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| customer_id | string | ❌ | 기존 고객 UUID (없으면 신규 고객 정보 필요) |
| customer_name | string | ❌ | 신규 고객명 (customer_id 없을 때 필수) |
| customer_phone | string | ❌ | 신규 고객 전화번호 |
| source_channel | string | ❌ | 유입 채널 |
| interest_product | string | ❌ | 관심 상품 |
| memo | string | ❌ | 메모 |

- **Response 201**: 생성된 리드 객체

---

### PATCH /api/v1/arki/leads/{id}/status
- **인증**: 필요
- **권한**: super_admin, arki_sales
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| status | string | ✅ | LeadStatus enum |
| notes | string | ❌ | 상태 변경 사유 |

- **Response 200**: 업데이트된 리드 객체
- **Error Codes**:
  - `INVALID_STATUS_TRANSITION` (422): 허용되지 않는 상태 전이

---

## 10. Arki - Consultations (상담)

### GET /api/v1/arki/consultations
- **인증**: 필요
- **권한**: super_admin, arki_sales, arki_store_manager
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| customer_id | string | ❌ | 고객 UUID 필터 |
| consultation_type | string | ❌ | 상담 유형 필터 |
| assigned_to | string | ❌ | 담당자 UUID 필터 |
| from_date | string | ❌ | ISO 8601 (consulted_at 기준) |
| to_date | string | ❌ | ISO 8601 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20 |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "customer_id": "uuid",
      "customer_name": "김철수",
      "lead_id": "uuid",
      "consultation_type": "방문",
      "consulted_at": "2026-03-10T14:00:00Z",
      "content": "소파 A형 3인용 상담 진행",
      "result": "계약 진행 예정",
      "next_action": "계약서 작성",
      "assigned_to": "uuid",
      "assigned_name": "홍길동",
      "contract_id": null,
      "created_at": "2026-03-10T14:30:00Z"
    }
  ],
  "meta": { "total": 50, "page": 1, "limit": 20 }
}
```

---

### POST /api/v1/arki/consultations
- **인증**: 필요
- **권한**: super_admin, arki_sales, arki_store_manager
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| customer_id | string | ✅ | 고객 UUID |
| lead_id | string | ❌ | 연결 리드 UUID |
| consultation_type | string | ✅ | 상담 유형 |
| consulted_at | string | ✅ | ISO 8601 상담 일시 |
| content | string | ✅ | 상담 내용 |
| result | string | ❌ | 상담 결과 |
| next_action | string | ❌ | 다음 액션 |
| assigned_to | string | ❌ | 담당자 UUID (미입력 시 요청자) |

- **Response 201**: 생성된 상담 객체

---

## 11. Arki - Contracts (계약)

### GET /api/v1/arki/contracts
- **인증**: 필요
- **권한**: super_admin, arki_store_manager
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| contract_status | string | ❌ | draft, signed, confirmed, cancelled |
| customer_id | string | ❌ | 고객 UUID 필터 |
| from_date | string | ❌ | ISO 8601 (contract_date 기준) |
| to_date | string | ❌ | ISO 8601 |
| q | string | ❌ | contract_number, 고객명 검색 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20 |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "contract_number": "CTR-2026-03-001",
      "customer_id": "uuid",
      "customer_name": "김철수",
      "consultation_id": "uuid",
      "contract_date": "2026-03-10",
      "contract_amount": "3500000.00",
      "deposit_amount": "500000.00",
      "contract_status": "confirmed",
      "delivery_required": true,
      "remarks": null,
      "created_by": "uuid",
      "created_at": "2026-03-10T15:00:00Z",
      "updated_at": "2026-03-11T10:00:00Z"
    }
  ],
  "meta": { "total": 80, "page": 1, "limit": 20 }
}
```

---

### POST /api/v1/arki/contracts
- **인증**: 필요
- **권한**: super_admin, arki_store_manager
- **Idempotency-Key**: 필수 (헤더)
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| customer_id | string | ✅ | 고객 UUID |
| consultation_id | string | ❌ | 연결 상담 UUID |
| contract_date | string | ✅ | 계약일 (YYYY-MM-DD) |
| contract_amount | number | ✅ | 계약 금액 |
| deposit_amount | number | ❌ | 입금 금액 |
| delivery_required | boolean | ❌ | 배송 필요 여부 (기본값 false) |
| remarks | string | ❌ | 비고 |

- **Response 201**: 생성된 계약 객체 (contract_number 자동 채번)
- **Error Codes**:
  - `DUPLICATE_IDEMPOTENCY_KEY` (409): 동일 Idempotency-Key 재요청

---

### PATCH /api/v1/arki/contracts/{id}/status
- **인증**: 필요
- **권한**: super_admin, arki_store_manager
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| status | string | ✅ | ContractStatus enum |
| remarks | string | ❌ | 취소 시 필수 |

- **Response 200**: 업데이트된 계약 객체
- **Error Codes**:
  - `INVALID_STATUS_TRANSITION` (422): 허용되지 않는 상태 전이
  - `CANCELLATION_REASON_REQUIRED` (422): confirmed → cancelled 시 remarks 미입력

---

## 12. Arki - Purchase Requests (발주 요청)

### GET /api/v1/arki/purchase-requests
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| status | string | ❌ | requested, reviewed, approved, rejected, converted_to_order |
| from_date | string | ❌ | ISO 8601 (created_at 기준) |
| to_date | string | ❌ | ISO 8601 |
| q | string | ❌ | 요청번호, 상품명 검색 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20 |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "request_number": "PR-2026-03-001",
      "supplier_name": "공급사A",
      "request_reason": "재고 부족",
      "desired_delivery_date": "2026-04-15",
      "total_amount": "5000000.00",
      "currency": "USD",
      "request_status": "requested",
      "items": [
        {
          "id": "uuid",
          "product_id": "uuid",
          "product_code": "PRD-001",
          "product_name": "소파 A형",
          "requested_qty": "10.0000",
          "unit_price": "500000.0000",
          "subtotal": "5000000.0000",
          "notes": null
        }
      ],
      "created_by": "uuid",
      "created_at": "2026-03-12T00:00:00Z"
    }
  ],
  "meta": { "total": 20, "page": 1, "limit": 20 }
}
```

---

### POST /api/v1/arki/purchase-requests
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Idempotency-Key**: 필수 (헤더)
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| supplier_name | string | ✅ | 공급사명 |
| request_reason | string | ❌ | 요청 사유 |
| desired_delivery_date | string | ❌ | 희망 납기일 (YYYY-MM-DD) |
| currency | string | ❌ | 통화 코드 (기본값 USD) |
| items | array | ✅ | 품목 목록 (최소 1개) |
| items[].product_id | string | ✅ | 상품 UUID |
| items[].requested_qty | number | ✅ | 요청 수량 |
| items[].unit_price | number | ✅ | 단가 |
| items[].notes | string | ❌ | 품목 비고 |

- **Response 201**: 생성된 발주 요청 객체 (items 포함)

---

### PATCH /api/v1/arki/purchase-requests/{id}/status
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| status | string | ✅ | PurchaseRequestStatus enum |
| rejection_reason | string | ❌ | rejected 시 필수 |

- **Response 200**: 업데이트된 발주 요청 객체
- **Error Codes**:
  - `INVALID_STATUS_TRANSITION` (422): 허용되지 않는 상태 전이
  - `REJECTION_REASON_REQUIRED` (422): rejected 시 rejection_reason 미입력

---

## 13. Arki - Purchase Orders (발주서)

### GET /api/v1/arki/purchase-orders
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| status | string | ❌ | created, ordered, invoiced, shipped, completed, cancelled |
| from_date | string | ❌ | ISO 8601 (order_date 기준) |
| to_date | string | ❌ | ISO 8601 |
| q | string | ❌ | 발주서번호, 공급사명 검색 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20 |

- **Response 200**: 발주서 목록 (items 배열 포함)

---

### POST /api/v1/arki/purchase-orders
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Idempotency-Key**: 필수 (헤더)
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| purchase_request_id | string | ❌ | 연결 발주 요청 UUID |
| supplier_name | string | ✅ | 공급사명 |
| order_date | string | ✅ | 발주일 (YYYY-MM-DD) |
| expected_delivery_date | string | ❌ | 납기 예정일 |
| currency | string | ❌ | 통화 코드 (기본값 USD) |
| notes | string | ❌ | 비고 |
| items | array | ✅ | 품목 목록 (최소 1개) |
| items[].product_id | string | ✅ | 상품 UUID |
| items[].ordered_qty | number | ✅ | 발주 수량 |
| items[].unit_price | number | ✅ | 단가 |

- **Response 201**: 생성된 발주서 객체 (items 포함)

---

### PATCH /api/v1/arki/purchase-orders/{id}/status
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| status | string | ✅ | PurchaseOrderStatus enum |
| cancellation_reason | string | ❌ | cancelled 시 필수 |

- **Response 200**: 업데이트된 발주서 객체
- **Error Codes**:
  - `INVALID_STATUS_TRANSITION` (422): 허용되지 않는 상태 전이
  - `CANCELLATION_REASON_REQUIRED` (422): cancelled 시 사유 미입력

---

## 14. Arki - Invoices (인보이스)

### GET /api/v1/arki/invoices
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| purchase_order_id | string | ❌ | 발주서 UUID 필터 |
| from_date | string | ❌ | ISO 8601 (invoice_date 기준) |
| to_date | string | ❌ | ISO 8601 |
| q | string | ❌ | 인보이스번호, 발주서번호 검색 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20 |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "invoice_number": "INV-2026-03-001",
      "purchase_order_id": "uuid",
      "purchase_order_number": "PO-2026-03-001",
      "supplier_name": "공급사A",
      "invoice_date": "2026-03-15",
      "invoice_amount": "5000000.00",
      "currency": "USD",
      "attachment_url": "https://storage.example.com/invoices/...",
      "created_at": "2026-03-15T10:00:00Z"
    }
  ],
  "meta": { "total": 15, "page": 1, "limit": 20 }
}
```

---

### POST /api/v1/arki/invoices
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| purchase_order_id | string | ✅ | 연결 발주서 UUID |
| invoice_number | string | ✅ | 인보이스 번호 |
| invoice_date | string | ✅ | 인보이스 일자 (YYYY-MM-DD) |
| invoice_amount | number | ✅ | 인보이스 금액 |
| currency | string | ❌ | 통화 코드 (기본값 USD) |
| attachment_key | string | ❌ | 업로드된 파일 스토리지 키 |

- **Response 201**: 생성된 인보이스 객체

---

## 15. Arki - Shipments (선적)

### GET /api/v1/arki/shipments
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| status | string | ❌ | pending, in_transit, arrived, completed |
| purchase_order_id | string | ❌ | 발주서 UUID 필터 |
| from_etd | string | ❌ | ETD 시작일 (YYYY-MM-DD) |
| to_eta | string | ❌ | ETA 종료일 (YYYY-MM-DD) |
| q | string | ❌ | BL번호, 발주서번호 검색 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20 |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "bl_number": "BL-2026-03-001",
      "purchase_order_id": "uuid",
      "carrier_name": "HMM",
      "vessel_name": "ARKI VESSEL",
      "etd": "2026-03-20",
      "eta": "2026-04-10",
      "shipment_status": "in_transit",
      "attachment_url": null,
      "created_at": "2026-03-18T00:00:00Z",
      "updated_at": "2026-03-20T00:00:00Z"
    }
  ],
  "meta": { "total": 10, "page": 1, "limit": 20 }
}
```

---

### POST /api/v1/arki/shipments
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| purchase_order_id | string | ✅ | 연결 발주서 UUID |
| bl_number | string | ✅ | BL 번호 |
| carrier_name | string | ❌ | 선사명 |
| vessel_name | string | ❌ | 선박명 |
| etd | string | ❌ | 출항 예정일 (YYYY-MM-DD) |
| eta | string | ❌ | 도착 예정일 (YYYY-MM-DD) |
| attachment_key | string | ❌ | BL 스캔본 스토리지 키 |

- **Response 201**: 생성된 선적 객체

---

### PATCH /api/v1/arki/shipments/{id}
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Request Body**: 부분 업데이트 (carrier_name, vessel_name, etd, eta, shipment_status, attachment_key)
- **Response 200**: 업데이트된 선적 객체

---

## 16. Arki - Deliveries (배송)

### GET /api/v1/arki/deliveries
- **인증**: 필요
- **권한**: super_admin, arki_logistics, arki_store_manager
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| delivery_status | string | ❌ | scheduled, confirmed, in_transit, completed, cancelled, delayed |
| delivery_date | string | ❌ | 특정 날짜 (YYYY-MM-DD) |
| delivery_team | string | ❌ | 배송팀 필터 |
| customer_id | string | ❌ | 고객 UUID 필터 |
| q | string | ❌ | delivery_number, 고객명, 주소 검색 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20 |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "delivery_number": "DEL-2026-03-001",
      "contract_id": "uuid",
      "customer_id": "uuid",
      "customer_name": "김철수",
      "delivery_date": "2026-03-20",
      "time_slot": "오전",
      "delivery_team": "A팀",
      "vehicle_code": "12가3456",
      "address_text": "서울시 강남구 ...",
      "ladder_required": false,
      "delivery_status": "scheduled",
      "created_at": "2026-03-12T00:00:00Z",
      "updated_at": "2026-03-12T00:00:00Z"
    }
  ],
  "meta": { "total": 30, "page": 1, "limit": 20 }
}
```

---

### POST /api/v1/arki/deliveries
- **인증**: 필요
- **권한**: super_admin, arki_store_manager
- **Idempotency-Key**: 필수 (헤더)
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| contract_id | string | ✅ | 연결 계약 UUID |
| delivery_date | string | ✅ | 배송일 (YYYY-MM-DD) |
| time_slot | string | ✅ | 오전, 오후, 종일 |
| delivery_team | string | ✅ | 배송팀명 |
| vehicle_code | string | ❌ | 차량 코드 |
| address_text | string | ✅ | 배송 주소 |
| ladder_required | boolean | ❌ | 사다리차 필요 여부 (기본값 false) |

- **Response 201**: 생성된 배송 객체
- **Error Codes**:
  - `CAPACITY_EXCEEDED` (422): CAPA 초과 (경고, 저장은 허용)

---

### PATCH /api/v1/arki/deliveries/{id}/status
- **인증**: 필요
- **권한**: super_admin, arki_logistics, arki_store_manager
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| status | string | ✅ | DeliveryStatus enum |
| reason | string | ❌ | delayed, cancelled 시 필수 |

- **Response 200**: 업데이트된 배송 객체
- **Error Codes**:
  - `INVALID_STATUS_TRANSITION` (422): 허용되지 않는 상태 전이
  - `REASON_REQUIRED` (422): delayed/cancelled 시 reason 미입력

---

## 17. Arki - Capacity Slots (배송 CAPA)

### GET /api/v1/arki/capacity-slots
- **인증**: 필요
- **권한**: super_admin, arki_logistics, arki_store_manager
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| slot_date | string | ❌ | 특정 날짜 (YYYY-MM-DD) |
| from_date | string | ❌ | 날짜 범위 시작 |
| to_date | string | ❌ | 날짜 범위 종료 |
| delivery_team | string | ❌ | 배송팀 필터 |
| slot_status | string | ❌ | open, limited, full, closed |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "slot_date": "2026-03-20",
      "delivery_team": "A팀",
      "time_slot": "오전",
      "max_capacity": 5,
      "used_capacity": 3,
      "remaining_capacity": 2,
      "slot_status": "limited",
      "created_at": "2026-03-01T00:00:00Z",
      "updated_at": "2026-03-12T00:00:00Z"
    }
  ],
  "meta": { "total": 30, "page": 1, "limit": 100 }
}
```

---

### POST /api/v1/arki/capacity-slots
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| slot_date | string | ✅ | 날짜 (YYYY-MM-DD) |
| delivery_team | string | ✅ | 배송팀명 |
| time_slot | string | ✅ | 오전, 오후, 종일 |
| max_capacity | integer | ✅ | 최대 CAPA |

- **Response 201**: 생성된 CAPA 슬롯 객체
- **Error Codes**:
  - `DUPLICATE_SLOT` (409): 동일 (slot_date, delivery_team, time_slot) 중복

---

### PATCH /api/v1/arki/capacity-slots/{id}
- **인증**: 필요
- **권한**: super_admin, arki_logistics
- **Request Body**: 부분 업데이트 (max_capacity, slot_status)
- **Response 200**: 업데이트된 CAPA 슬롯 객체

---

## 18. Arki - Happy Calls (해피콜)

### GET /api/v1/arki/happy-calls
- **인증**: 필요
- **권한**: super_admin, arki_store_manager
- **Query Params**:

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| call_type | string | ❌ | pre_delivery, post_delivery |
| call_result | string | ❌ | success, no_answer, rescheduled, cancelled |
| delivery_id | string | ❌ | 배송 UUID 필터 |
| from_date | string | ❌ | ISO 8601 (called_at 기준) |
| to_date | string | ❌ | ISO 8601 |
| q | string | ❌ | 고객명, 배송번호 검색 |
| page | integer | ❌ | 기본값 1 |
| limit | integer | ❌ | 기본값 20 |

- **Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "delivery_id": "uuid",
      "delivery_number": "DEL-2026-03-001",
      "customer_id": "uuid",
      "customer_name": "김철수",
      "call_type": "pre_delivery",
      "called_at": "2026-03-18T10:00:00Z",
      "call_result": "success",
      "call_content": "배송 일정 확인 완료",
      "next_action": null,
      "rescheduled_at": null,
      "assigned_to": "uuid",
      "assigned_name": "홍길동",
      "created_at": "2026-03-18T10:30:00Z"
    }
  ],
  "meta": { "total": 25, "page": 1, "limit": 20 }
}
```

---

### POST /api/v1/arki/happy-calls
- **인증**: 필요
- **권한**: super_admin, arki_store_manager
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| delivery_id | string | ✅ | 연결 배송 UUID |
| call_type | string | ✅ | pre_delivery, post_delivery |
| called_at | string | ✅ | ISO 8601 통화 일시 |
| call_result | string | ✅ | success, no_answer, rescheduled, cancelled |
| call_content | string | ❌ | 통화 내용 |
| next_action | string | ❌ | 다음 액션 |
| rescheduled_at | string | ❌ | 재예약 일시 (rescheduled 시 필수) |

- **Response 201**: 생성된 해피콜 객체
- **Error Codes**:
  - `RESCHEDULED_AT_REQUIRED` (422): call_result=rescheduled 시 rescheduled_at 미입력

---

## 19. Error Reports (오류 신고)

> 상세 명세는 [4. Ops - Logs](#4-ops---logs-로그-관리) 섹션의 `POST /api/v1/ops/error-reports` 및 `GET /api/v1/ops/error-reports` 참조.

### GET /api/v1/ops/error-reports/{id}
- **인증**: 필요
- **권한**: super_admin, ops_admin, support_operator
- **Response 200**: 오류 신고 단건 상세 (user_context JSONB 포함, error_message 원본은 super_admin만 노출)

---

## 20. Files (파일 업로드)

### POST /api/v1/files/presign
- **인증**: 필요
- **권한**: super_admin, ops_admin, arki_logistics, arki_sales, arki_store_manager
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| filename | string | ✅ | 원본 파일명 |
| content_type | string | ✅ | MIME 타입 (예: application/pdf, image/jpeg) |
| target_entity | string | ✅ | 연결 엔티티 (contracts, invoices, shipments 등) |
| entity_id | string | ❌ | 연결 엔티티 UUID (기존 레코드 연결 시) |

- **Response 200**:
```json
{
  "data": {
    "upload_url": "https://storage.example.com/presigned-upload-url?...",
    "storage_key": "uploads/contracts/2026/03/uuid-filename.pdf",
    "expires_in": 900
  }
}
```
- **비고**: 클라이언트는 upload_url로 직접 PUT 요청하여 파일 업로드. storage_key를 이후 API 요청의 attachment_key 필드에 사용.

---

## 21. Sync (시트 동기화)

### POST /api/v1/sync/jobs
- **인증**: 필요
- **권한**: super_admin, ops_admin, arki_logistics, arki_sales, arki_store_manager
- **Request Body**:

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| project_code | string | ✅ | 프로젝트 코드 |
| sheet_name | string | ✅ | Google Sheets 시트명 |
| dataset | string | ✅ | 동기화 대상 데이터셋 (products, inventory, contracts 등) |
| job_type | string | ✅ | export (DB→Sheet), import (Sheet→DB) |
| idempotency_key | string | ❌ | 중복 실행 방지 키 |

- **Response 202**:
```json
{
  "data": {
    "id": "uuid",
    "project_code": "ARKI",
    "sheet_name": "재고현황",
    "dataset": "inventory",
    "job_type": "export",
    "job_status": "pending",
    "result_url": null,
    "created_at": "2026-03-12T10:00:00Z"
  }
}
```

---

### GET /api/v1/sync/jobs/{id}
- **인증**: 필요
- **권한**: super_admin, ops_admin, arki_logistics, arki_sales, arki_store_manager
- **Response 200**:
```json
{
  "data": {
    "id": "uuid",
    "project_code": "ARKI",
    "sheet_name": "재고현황",
    "dataset": "inventory",
    "job_type": "export",
    "job_status": "completed",
    "result_url": "https://docs.google.com/spreadsheets/d/...",
    "error_message": null,
    "created_at": "2026-03-12T10:00:00Z",
    "updated_at": "2026-03-12T10:02:00Z"
  }
}
```
- **job_status 값**: pending, running, completed, failed

---

*최종 업데이트: 2026-03-12*
