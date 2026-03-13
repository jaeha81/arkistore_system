# 06 ERD STANDARD — Arkistore Operations Automation System

엔티티 관계 다이어그램, 도메인 경계 규칙, 인덱스 설계 기준, FK 제약 규칙을 정의한다.

---

## 목차

1. [운영 도메인 ERD](#1-운영-도메인-erd)
2. [업무 도메인 ERD](#2-업무-도메인-erd)
3. [도메인 간 경계 규칙](#3-도메인-간-경계-규칙)
4. [인덱스 설계 기준](#4-인덱스-설계-기준)
5. [FK 제약 규칙](#5-fk-제약-규칙)

---

## 1. 운영 도메인 ERD

### 1-1. 엔티티 관계 다이어그램

```
users
  │
  ├──────────────────────< admin_actions (actor_user_id)
  │
  ├──────────────────────< github_issues (created_by)
  │
  ├──────────────────────< sheet_sync_jobs (created_by)
  │
  └──────────────────────< deployment_records (deployed_by)


projects
  │
  ├──────────────────────< project_sites (project_id)
  │
  └──────────────────────< deployment_records (project_id)


project_sites
  │
  └──────────────────────< deployment_records (site_id, nullable)


error_reports
  │
  └──────────────────────> issue_groups (issue_group_id, nullable FK)


issue_groups
  │
  └──────────────────────< github_issues (issue_group_id)
```

### 1-2. 엔티티 상세

#### users
```
┌─────────────────────────────────────────┐
│ users                                   │
├─────────────────────────────────────────┤
│ PK  id              UUID                │
│     email           VARCHAR(255) UNIQUE │
│     name            VARCHAR(100)        │
│     hashed_password TEXT                │
│     role            VARCHAR(50)         │
│     is_active       BOOLEAN             │
│     created_at      TIMESTAMPTZ         │
│     updated_at      TIMESTAMPTZ         │
│     deleted_at      TIMESTAMPTZ NULL    │
└─────────────────────────────────────────┘
```

#### projects
```
┌─────────────────────────────────────────┐
│ projects                                │
├─────────────────────────────────────────┤
│ PK  id              UUID                │
│     project_code    VARCHAR(50) UNIQUE  │
│     name            VARCHAR(200)        │
│     client_name     VARCHAR(200)        │
│     service_type    VARCHAR(100)        │
│     main_url        VARCHAR(500)        │
│     status          ENUM(ProjectStatus) │
│     operation_mode  ENUM(OperationMode) │
│     created_at      TIMESTAMPTZ         │
│     updated_at      TIMESTAMPTZ         │
│     deleted_at      TIMESTAMPTZ NULL    │
└─────────────────────────────────────────┘
```

#### project_sites
```
┌─────────────────────────────────────────┐
│ project_sites                           │
├─────────────────────────────────────────┤
│ PK  id              UUID                │
│ FK  project_id      UUID → projects     │
│     site_code       VARCHAR UNIQUE      │
│     site_name       VARCHAR             │
│     site_url        VARCHAR             │
│     site_type       ENUM(SiteType)      │
│     is_enabled      BOOLEAN             │
│     created_at      TIMESTAMPTZ         │
│     updated_at      TIMESTAMPTZ         │
└─────────────────────────────────────────┘
```

#### error_reports
```
┌──────────────────────────────────────────────┐
│ error_reports                                │
├──────────────────────────────────────────────┤
│ PK  id                   UUID                │
│     project_code         VARCHAR INDEX       │
│     site_type            ENUM(SiteType)      │
│     environment          ENUM(Environment)   │
│     app_version          VARCHAR             │
│     screen_name          VARCHAR NULL        │
│     error_code           VARCHAR INDEX       │
│     error_message        TEXT                │
│     error_message_masked TEXT NULL           │
│     user_context         JSONB NULL          │
│     report_status        ENUM(IssueStatus)   │
│ FK  issue_group_id       UUID → issue_groups NULL │
│     trace_id             VARCHAR NULL        │
│     occurred_at          TIMESTAMPTZ         │
│     created_at           TIMESTAMPTZ         │
└──────────────────────────────────────────────┘
```

#### issue_groups
```
┌──────────────────────────────────────────────┐
│ issue_groups                                 │
├──────────────────────────────────────────────┤
│ PK  id               UUID                    │
│     group_key        VARCHAR UNIQUE INDEX    │
│     group_title      VARCHAR                 │
│     occurrence_count INTEGER                 │
│     first_seen_at    TIMESTAMPTZ             │
│     last_seen_at     TIMESTAMPTZ             │
│     group_status     ENUM(IssueStatus)       │
│ FK  github_issue_id  UUID → github_issues NULL │
│     created_at       TIMESTAMPTZ             │
│     updated_at       TIMESTAMPTZ             │
└──────────────────────────────────────────────┘
```

#### github_issues
```
┌──────────────────────────────────────────────┐
│ github_issues                                │
├──────────────────────────────────────────────┤
│ PK  id                    UUID               │
│ FK  issue_group_id        UUID → issue_groups │
│     repository            VARCHAR            │
│     github_issue_number   INTEGER            │
│     github_issue_url      VARCHAR            │
│     state                 VARCHAR            │
│ FK  created_by            UUID → users NULL  │
│     created_at            TIMESTAMPTZ        │
│     updated_at            TIMESTAMPTZ        │
└──────────────────────────────────────────────┘
```

#### event_logs
```
┌──────────────────────────────────────────────┐
│ event_logs                                   │
├──────────────────────────────────────────────┤
│ PK  id            UUID                       │
│     project_code  VARCHAR INDEX              │
│     environment   ENUM(Environment)          │
│     app_version   VARCHAR                    │
│     event_type    VARCHAR INDEX              │
│     event_name    VARCHAR                    │
│     payload       JSONB NULL                 │
│     logged_at     TIMESTAMPTZ                │
└──────────────────────────────────────────────┘
```
> event_logs는 append-only 로그 테이블. FK 없음. 고성능 삽입 우선.

#### admin_actions
```
┌──────────────────────────────────────────────┐
│ admin_actions                                │
├──────────────────────────────────────────────┤
│ PK  id             UUID                      │
│ FK  actor_user_id  UUID → users NULL         │
│     action_type    VARCHAR INDEX             │
│     target_table   VARCHAR                   │
│     target_id      UUID NULL                 │
│     before_data    JSONB NULL                │
│     after_data     JSONB NULL                │
│     ip_address     VARCHAR NULL              │
│     notes          TEXT NULL                 │
│     created_at     TIMESTAMPTZ               │
└──────────────────────────────────────────────┘
```
> admin_actions는 감사 로그. 삭제 불가. actor_user_id는 SET NULL (계정 삭제 시 보존).

#### deployment_records
```
┌──────────────────────────────────────────────┐
│ deployment_records                           │
├──────────────────────────────────────────────┤
│ PK  id             UUID                      │
│ FK  project_id     UUID → projects           │
│ FK  site_id        UUID → project_sites NULL │
│     environment    ENUM(Environment)         │
│     version_tag    VARCHAR                   │
│ FK  deployed_by    UUID → users NULL         │
│     deploy_notes   TEXT NULL                 │
│     deployed_at    TIMESTAMPTZ               │
│     status         VARCHAR                   │
└──────────────────────────────────────────────┘
```

#### sheet_sync_jobs
```
┌──────────────────────────────────────────────┐
│ sheet_sync_jobs                              │
├──────────────────────────────────────────────┤
│ PK  id               UUID                    │
│     project_code     VARCHAR                 │
│     sheet_name       VARCHAR                 │
│     dataset          VARCHAR                 │
│     job_type         VARCHAR                 │
│     job_status       ENUM(SyncJobStatus)     │
│     result_url       VARCHAR NULL            │
│     error_message    TEXT NULL               │
│     idempotency_key  VARCHAR UNIQUE NULL      │
│ FK  created_by       UUID → users NULL       │
│     created_at       TIMESTAMPTZ             │
│     updated_at       TIMESTAMPTZ             │
└──────────────────────────────────────────────┘
```

---

## 2. 업무 도메인 ERD

### 2-1. 엔티티 관계 다이어그램

```
products
  │
  └──────────────────────< inventories (product_id, UNIQUE — 상품당 1개)
  │
  └──────────────────────< purchase_request_items (product_id)
  │
  └──────────────────────< purchase_order_items (product_id)


customers
  │
  ├──────────────────────< leads (customer_id)
  │
  ├──────────────────────< consultations (customer_id)
  │
  ├──────────────────────< contracts (customer_id)
  │
  └──────────────────────< deliveries (customer_id)


leads
  │
  └──────────────────────< consultations (lead_id, nullable)


consultations
  │
  └──────────────────────< contracts (consultation_id, nullable)


contracts
  │
  └──────────────────────< deliveries (contract_id)


purchase_requests
  │
  ├──────────────────────< purchase_request_items (purchase_request_id)
  │
  └──────────────────────< purchase_orders (purchase_request_id, nullable)


purchase_orders
  │
  ├──────────────────────< purchase_order_items (purchase_order_id)
  │
  ├──────────────────────< invoices (purchase_order_id)
  │
  └──────────────────────< shipments (purchase_order_id)


deliveries
  │
  ├──────────────────────< happy_calls (delivery_id)
  │
  └──────────────────────> capacity_slots (slot_date + delivery_team + time_slot 참조, 논리적 연결)


attachments
  │
  └──────────────────────> (contracts, invoices, shipments 등 다형성 참조)
```

### 2-2. 엔티티 상세

#### products
```
┌──────────────────────────────────────────────┐
│ products                                     │
├──────────────────────────────────────────────┤
│ PK  id             UUID                      │
│     brand_name     VARCHAR                   │
│     product_code   VARCHAR UNIQUE            │
│     product_name   VARCHAR                   │
│     category_name  VARCHAR NULL              │
│     option_text    VARCHAR NULL              │
│     unit_price     NUMERIC(12,4)             │
│     currency       VARCHAR(3)                │
│     supplier_name  VARCHAR NULL              │
│     is_active      BOOLEAN                   │
│     created_at     TIMESTAMPTZ               │
│     updated_at     TIMESTAMPTZ               │
│     deleted_at     TIMESTAMPTZ NULL          │
└──────────────────────────────────────────────┘
```

#### inventories
```
┌──────────────────────────────────────────────┐
│ inventories                                  │
├──────────────────────────────────────────────┤
│ PK  id                    UUID               │
│ FK  product_id            UUID → products UNIQUE │
│     warehouse_name        VARCHAR            │
│     current_stock         NUMERIC(12,4)      │
│     reserved_stock        NUMERIC(12,4)      │
│     available_stock       NUMERIC(12,4)      │
│     safety_stock          NUMERIC(12,4)      │
│     expected_inbound_date DATE NULL          │
│     inventory_status      ENUM(InventoryStatus) │
│     created_at            TIMESTAMPTZ        │
│     updated_at            TIMESTAMPTZ        │
└──────────────────────────────────────────────┘
```

#### customers
```
┌──────────────────────────────────────────────┐
│ customers                                    │
├──────────────────────────────────────────────┤
│ PK  id               UUID                    │
│     customer_type    VARCHAR                 │
│     name             VARCHAR                 │
│     phone            VARCHAR NULL (암호화)   │
│     phone_masked     VARCHAR NULL            │
│     email            VARCHAR NULL (암호화)   │
│     email_masked     VARCHAR NULL            │
│     region           VARCHAR NULL            │
│     source_channel   VARCHAR NULL            │
│     grade            ENUM(CustomerGrade)     │
│     is_vip           BOOLEAN                 │
│     created_at       TIMESTAMPTZ             │
│     updated_at       TIMESTAMPTZ             │
│     deleted_at       TIMESTAMPTZ NULL        │
└──────────────────────────────────────────────┘
```

#### leads
```
┌──────────────────────────────────────────────┐
│ leads                                        │
├──────────────────────────────────────────────┤
│ PK  id               UUID                    │
│ FK  customer_id      UUID → customers        │
│     source_channel   VARCHAR NULL            │
│     interest_product VARCHAR NULL            │
│     lead_status      ENUM(LeadStatus)        │
│     memo             TEXT NULL               │
│     created_at       TIMESTAMPTZ             │
│     updated_at       TIMESTAMPTZ             │
│     deleted_at       TIMESTAMPTZ NULL        │
└──────────────────────────────────────────────┘
```

#### consultations
```
┌──────────────────────────────────────────────┐
│ consultations                                │
├──────────────────────────────────────────────┤
│ PK  id                  UUID                 │
│ FK  customer_id         UUID → customers     │
│ FK  lead_id             UUID → leads NULL    │
│     consultation_type   VARCHAR              │
│     consulted_at        TIMESTAMPTZ          │
│     content             TEXT                 │
│     result              TEXT NULL            │
│     next_action         TEXT NULL            │
│ FK  assigned_to         UUID → users NULL    │
│     created_at          TIMESTAMPTZ          │
│     updated_at          TIMESTAMPTZ          │
└──────────────────────────────────────────────┘
```
> assigned_to는 운영 도메인 users 참조. 도메인 간 참조 허용 예외 (읽기 전용 참조).

#### contracts
```
┌──────────────────────────────────────────────┐
│ contracts                                    │
├──────────────────────────────────────────────┤
│ PK  id                UUID                   │
│     contract_number   VARCHAR UNIQUE NULL     │
│ FK  customer_id       UUID → customers       │
│ FK  consultation_id   UUID → consultations NULL │
│     contract_date     DATE                   │
│     contract_amount   NUMERIC(14,2)          │
│     deposit_amount    NUMERIC(14,2) NULL      │
│     contract_status   ENUM(ContractStatus)   │
│     delivery_required BOOLEAN                │
│     remarks           TEXT NULL              │
│ FK  created_by        UUID → users NULL      │
│     idempotency_key   VARCHAR UNIQUE NULL     │
│     created_at        TIMESTAMPTZ            │
│     updated_at        TIMESTAMPTZ            │
│     deleted_at        TIMESTAMPTZ NULL       │
└──────────────────────────────────────────────┘
```

#### purchase_requests
```
┌──────────────────────────────────────────────┐
│ purchase_requests                            │
├──────────────────────────────────────────────┤
│ PK  id                    UUID               │
│     request_number        VARCHAR UNIQUE NULL │
│     supplier_name         VARCHAR            │
│     request_reason        TEXT NULL          │
│     desired_delivery_date DATE NULL          │
│     total_amount          NUMERIC(14,2)      │
│     currency              VARCHAR(3)         │
│     request_status        ENUM(PurchaseRequestStatus) │
│ FK  created_by            UUID → users NULL  │
│     idempotency_key       VARCHAR UNIQUE NULL │
│     created_at            TIMESTAMPTZ        │
│     updated_at            TIMESTAMPTZ        │
└──────────────────────────────────────────────┘
```

#### purchase_request_items
```
┌──────────────────────────────────────────────┐
│ purchase_request_items                       │
├──────────────────────────────────────────────┤
│ PK  id                   UUID                │
│ FK  purchase_request_id  UUID → purchase_requests │
│ FK  product_id           UUID → products     │
│     requested_qty        NUMERIC(12,4)       │
│     unit_price           NUMERIC(12,4)       │
│     subtotal             NUMERIC(14,2)       │
│     notes                TEXT NULL           │
│     created_at           TIMESTAMPTZ         │
└──────────────────────────────────────────────┘
```

#### purchase_orders
```
┌──────────────────────────────────────────────┐
│ purchase_orders                              │
├──────────────────────────────────────────────┤
│ PK  id                      UUID             │
│     order_number            VARCHAR UNIQUE NULL │
│ FK  purchase_request_id     UUID → purchase_requests NULL │
│     supplier_name           VARCHAR          │
│     order_date              DATE             │
│     expected_delivery_date  DATE NULL        │
│     total_amount            NUMERIC(14,2)    │
│     currency                VARCHAR(3)       │
│     order_status            ENUM(PurchaseOrderStatus) │
│     notes                   TEXT NULL        │
│ FK  created_by              UUID → users NULL │
│     idempotency_key         VARCHAR UNIQUE NULL │
│     created_at              TIMESTAMPTZ      │
│     updated_at              TIMESTAMPTZ      │
└──────────────────────────────────────────────┘
```

#### purchase_order_items
```
┌──────────────────────────────────────────────┐
│ purchase_order_items                         │
├──────────────────────────────────────────────┤
│ PK  id                  UUID                 │
│ FK  purchase_order_id   UUID → purchase_orders │
│ FK  product_id          UUID → products      │
│     ordered_qty         NUMERIC(12,4)        │
│     unit_price          NUMERIC(12,4)        │
│     subtotal            NUMERIC(14,2)        │
│     created_at          TIMESTAMPTZ          │
└──────────────────────────────────────────────┘
```

#### invoices
```
┌──────────────────────────────────────────────┐
│ invoices                                     │
├──────────────────────────────────────────────┤
│ PK  id                  UUID                 │
│     invoice_number      VARCHAR UNIQUE       │
│ FK  purchase_order_id   UUID → purchase_orders │
│     supplier_name       VARCHAR              │
│     invoice_date        DATE                 │
│     invoice_amount      NUMERIC(14,2)        │
│     currency            VARCHAR(3)           │
│     attachment_key      VARCHAR NULL         │
│     created_at          TIMESTAMPTZ          │
│     updated_at          TIMESTAMPTZ          │
└──────────────────────────────────────────────┘
```

#### shipments
```
┌──────────────────────────────────────────────┐
│ shipments                                    │
├──────────────────────────────────────────────┤
│ PK  id                  UUID                 │
│     bl_number           VARCHAR UNIQUE       │
│ FK  purchase_order_id   UUID → purchase_orders │
│     carrier_name        VARCHAR NULL         │
│     vessel_name         VARCHAR NULL         │
│     etd                 DATE NULL            │
│     eta                 DATE NULL            │
│     shipment_status     ENUM(ShipmentStatus) │
│     attachment_key      VARCHAR NULL         │
│     created_at          TIMESTAMPTZ          │
│     updated_at          TIMESTAMPTZ          │
└──────────────────────────────────────────────┘
```

#### deliveries
```
┌──────────────────────────────────────────────┐
│ deliveries                                   │
├──────────────────────────────────────────────┤
│ PK  id               UUID                    │
│     delivery_number  VARCHAR UNIQUE NULL      │
│ FK  contract_id      UUID → contracts        │
│ FK  customer_id      UUID → customers        │
│     delivery_date    DATE                    │
│     time_slot        VARCHAR                 │
│     delivery_team    VARCHAR                 │
│     vehicle_code     VARCHAR NULL            │
│     address_text     TEXT                    │
│     ladder_required  BOOLEAN                 │
│     delivery_status  ENUM(DeliveryStatus)    │
│     idempotency_key  VARCHAR UNIQUE NULL      │
│     created_at       TIMESTAMPTZ             │
│     updated_at       TIMESTAMPTZ             │
└──────────────────────────────────────────────┘
```

#### capacity_slots
```
┌──────────────────────────────────────────────┐
│ capacity_slots                               │
├──────────────────────────────────────────────┤
│ PK  id                  UUID                 │
│     slot_date           DATE                 │
│     delivery_team       VARCHAR              │
│     time_slot           VARCHAR              │
│     max_capacity        INTEGER              │
│     used_capacity       INTEGER              │
│     remaining_capacity  INTEGER              │
│     slot_status         ENUM(SlotStatus)     │
│     UNIQUE(slot_date, delivery_team, time_slot) │
│     created_at          TIMESTAMPTZ          │
│     updated_at          TIMESTAMPTZ          │
└──────────────────────────────────────────────┘
```

#### happy_calls
```
┌──────────────────────────────────────────────┐
│ happy_calls                                  │
├──────────────────────────────────────────────┤
│ PK  id               UUID                    │
│ FK  delivery_id      UUID → deliveries       │
│ FK  customer_id      UUID → customers        │
│     call_type        VARCHAR                 │
│     called_at        TIMESTAMPTZ             │
│     call_result      VARCHAR                 │
│     call_content     TEXT NULL               │
│     next_action      TEXT NULL               │
│     rescheduled_at   TIMESTAMPTZ NULL        │
│ FK  assigned_to      UUID → users NULL       │
│     created_at       TIMESTAMPTZ             │
│     updated_at       TIMESTAMPTZ             │
└──────────────────────────────────────────────┘
```

#### attachments
```
┌──────────────────────────────────────────────┐
│ attachments                                  │
├──────────────────────────────────────────────┤
│ PK  id               UUID                    │
│     entity_type      VARCHAR INDEX           │
│     entity_id        UUID INDEX              │
│     filename         VARCHAR                 │
│     storage_key      VARCHAR                 │
│     content_type     VARCHAR                 │
│     file_size        BIGINT NULL             │
│ FK  uploaded_by      UUID → users NULL       │
│     created_at       TIMESTAMPTZ             │
└──────────────────────────────────────────────┘
```
> attachments는 다형성 참조 패턴. entity_type + entity_id 복합 인덱스 필수.

---

## 3. 도메인 간 경계 규칙

### 3-1. 원칙

```
┌─────────────────────────────────────────────────────────────┐
│  운영 도메인 (ops)          업무 도메인 (arki)               │
│  ─────────────────          ──────────────────               │
│  users                      products                         │
│  projects                   inventories                      │
│  project_sites              customers                        │
│  error_reports              leads                            │
│  issue_groups               consultations                    │
│  github_issues              contracts                        │
│  event_logs                 purchase_requests                │
│  admin_actions              purchase_request_items           │
│  deployment_records         purchase_orders                  │
│  sheet_sync_jobs            purchase_order_items             │
│                             invoices                         │
│                             shipments                        │
│                             deliveries                       │
│                             capacity_slots                   │
│                             happy_calls                      │
│                             attachments                      │
└─────────────────────────────────────────────────────────────┘
```

### 3-2. 허용되는 도메인 간 참조

| 참조 방향 | 테이블 | 참조 대상 | 허용 이유 |
|-----------|--------|-----------|-----------|
| 업무 → 운영 | contracts.created_by | users.id | 생성자 추적 (감사 목적) |
| 업무 → 운영 | consultations.assigned_to | users.id | 담당자 지정 (읽기 전용) |
| 업무 → 운영 | happy_calls.assigned_to | users.id | 담당자 지정 (읽기 전용) |
| 업무 → 운영 | purchase_requests.created_by | users.id | 생성자 추적 |
| 업무 → 운영 | purchase_orders.created_by | users.id | 생성자 추적 |
| 업무 → 운영 | sheet_sync_jobs.created_by | users.id | 생성자 추적 |
| 업무 → 운영 | attachments.uploaded_by | users.id | 업로더 추적 |

> **규칙**: 업무 도메인 → 운영 도메인 방향의 users 참조만 허용. 운영 도메인 테이블이 업무 도메인 테이블을 직접 FK로 참조하는 것은 금지.

### 3-3. 금지되는 도메인 간 참조

| 금지 패턴 | 이유 |
|-----------|------|
| projects → contracts | 운영 도메인이 업무 데이터에 의존하면 안 됨 |
| error_reports → customers | 오류 신고는 project_code 기반 연결만 허용 |
| issue_groups → deliveries | 도메인 분리 원칙 위반 |
| deployment_records → purchase_orders | 무관한 도메인 간 결합 금지 |

### 3-4. 간접 연결 허용 패턴

- 운영 도메인에서 업무 데이터를 조회할 때는 **project_code** 또는 **API 호출**을 통해 간접 참조
- 직접 JOIN 쿼리로 도메인 경계를 넘는 것은 금지 (서비스 레이어에서 분리 조회)

---

## 4. 인덱스 설계 기준

### 4-1. 운영 도메인 인덱스

| 테이블 | 컬럼 | 인덱스 유형 | 이유 |
|--------|------|-------------|------|
| users | email | UNIQUE INDEX | 로그인 조회 |
| users | role | INDEX | 역할별 필터링 |
| projects | project_code | UNIQUE INDEX | 코드 기반 조회 |
| projects | status | INDEX | 상태 필터링 |
| project_sites | project_id | INDEX | 프로젝트별 사이트 조회 |
| project_sites | site_code | UNIQUE INDEX | 코드 기반 조회 |
| error_reports | project_code | INDEX | 프로젝트별 오류 조회 |
| error_reports | error_code | INDEX | 오류 코드 기반 그룹핑 |
| error_reports | report_status | INDEX | 상태별 필터링 |
| error_reports | occurred_at | INDEX | 시간 범위 조회 |
| error_reports | issue_group_id | INDEX | 그룹 연결 조회 |
| issue_groups | group_key | UNIQUE INDEX | 그룹 키 중복 방지 |
| issue_groups | group_status | INDEX | 상태별 필터링 |
| issue_groups | last_seen_at | INDEX | 최신 이슈 정렬 |
| event_logs | project_code | INDEX | 프로젝트별 로그 조회 |
| event_logs | event_type | INDEX | 이벤트 타입 필터링 |
| event_logs | logged_at | INDEX | 시간 범위 조회 |
| admin_actions | actor_user_id | INDEX | 사용자별 액션 조회 |
| admin_actions | action_type | INDEX | 액션 타입 필터링 |
| admin_actions | created_at | INDEX | 시간 범위 조회 |
| deployment_records | project_id | INDEX | 프로젝트별 배포 조회 |
| deployment_records | deployed_at | INDEX | 시간 범위 조회 |
| sheet_sync_jobs | idempotency_key | UNIQUE INDEX | 중복 실행 방지 |

### 4-2. 업무 도메인 인덱스

| 테이블 | 컬럼 | 인덱스 유형 | 이유 |
|--------|------|-------------|------|
| products | product_code | UNIQUE INDEX | 코드 기반 조회 |
| products | is_active | INDEX | 활성 상품 필터링 |
| products | brand_name | INDEX | 브랜드별 필터링 |
| inventories | product_id | UNIQUE INDEX | 상품당 1개 재고 보장 |
| inventories | inventory_status | INDEX | 재고 상태 필터링 |
| customers | name | INDEX | 이름 검색 |
| customers | grade | INDEX | 등급별 필터링 |
| customers | is_vip | INDEX | VIP 필터링 |
| leads | customer_id | INDEX | 고객별 리드 조회 |
| leads | lead_status | INDEX | 상태별 필터링 |
| leads | created_at | INDEX | 시간 범위 조회 |
| consultations | customer_id | INDEX | 고객별 상담 조회 |
| consultations | lead_id | INDEX | 리드별 상담 조회 |
| contracts | customer_id | INDEX | 고객별 계약 조회 |
| contracts | contract_status | INDEX | 상태별 필터링 |
| contracts | contract_date | INDEX | 날짜 범위 조회 |
| contracts | idempotency_key | UNIQUE INDEX | 중복 생성 방지 |
| purchase_requests | request_status | INDEX | 상태별 필터링 |
| purchase_requests | created_at | INDEX | 시간 범위 조회 |
| purchase_requests | idempotency_key | UNIQUE INDEX | 중복 생성 방지 |
| purchase_request_items | purchase_request_id | INDEX | 발주요청별 품목 조회 |
| purchase_request_items | product_id | INDEX | 상품별 발주요청 조회 |
| purchase_orders | order_status | INDEX | 상태별 필터링 |
| purchase_orders | purchase_request_id | INDEX | 발주요청 연결 조회 |
| purchase_orders | idempotency_key | UNIQUE INDEX | 중복 생성 방지 |
| purchase_order_items | purchase_order_id | INDEX | 발주서별 품목 조회 |
| invoices | purchase_order_id | INDEX | 발주서별 인보이스 조회 |
| invoices | invoice_date | INDEX | 날짜 범위 조회 |
| shipments | purchase_order_id | INDEX | 발주서별 선적 조회 |
| shipments | shipment_status | INDEX | 상태별 필터링 |
| shipments | eta | INDEX | ETA 기준 조회 |
| deliveries | contract_id | INDEX | 계약별 배송 조회 |
| deliveries | customer_id | INDEX | 고객별 배송 조회 |
| deliveries | delivery_date | INDEX | 날짜 기준 조회 (핵심) |
| deliveries | delivery_status | INDEX | 상태별 필터링 |
| deliveries | delivery_team | INDEX | 팀별 배송 조회 |
| deliveries | idempotency_key | UNIQUE INDEX | 중복 예약 방지 |
| capacity_slots | (slot_date, delivery_team, time_slot) | UNIQUE INDEX | 슬롯 중복 방지 |
| capacity_slots | slot_date | INDEX | 날짜 기준 조회 |
| capacity_slots | slot_status | INDEX | 상태별 필터링 |
| happy_calls | delivery_id | INDEX | 배송별 해피콜 조회 |
| happy_calls | customer_id | INDEX | 고객별 해피콜 조회 |
| happy_calls | called_at | INDEX | 시간 범위 조회 |
| attachments | (entity_type, entity_id) | COMPOSITE INDEX | 다형성 참조 조회 |

---

## 5. FK 제약 규칙

### 5-1. ON DELETE 동작 기준

| 관계 | FK 컬럼 | ON DELETE | 이유 |
|------|---------|-----------|------|
| projects → project_sites | project_sites.project_id | RESTRICT | 사이트가 있는 프로젝트 삭제 방지 |
| projects → deployment_records | deployment_records.project_id | RESTRICT | 배포 기록 보존 |
| project_sites → deployment_records | deployment_records.site_id | SET NULL | 사이트 삭제 시 배포 기록 보존 |
| users → admin_actions | admin_actions.actor_user_id | SET NULL | 감사 로그 보존 (계정 삭제 후에도) |
| users → github_issues | github_issues.created_by | SET NULL | 이슈 기록 보존 |
| users → deployment_records | deployment_records.deployed_by | SET NULL | 배포 기록 보존 |
| users → sheet_sync_jobs | sheet_sync_jobs.created_by | SET NULL | 동기화 기록 보존 |
| issue_groups → error_reports | error_reports.issue_group_id | SET NULL | 그룹 삭제 시 신고 보존 |
| issue_groups → github_issues | github_issues.issue_group_id | RESTRICT | 이슈 그룹 삭제 전 GitHub 이슈 처리 필요 |
| products → inventories | inventories.product_id | RESTRICT | 재고가 있는 상품 삭제 방지 |
| products → purchase_request_items | purchase_request_items.product_id | RESTRICT | 발주 이력 보존 |
| products → purchase_order_items | purchase_order_items.product_id | RESTRICT | 발주서 이력 보존 |
| customers → leads | leads.customer_id | RESTRICT | 리드가 있는 고객 삭제 방지 |
| customers → consultations | consultations.customer_id | RESTRICT | 상담 이력 보존 |
| customers → contracts | contracts.customer_id | RESTRICT | 계약이 있는 고객 삭제 방지 |
| customers → deliveries | deliveries.customer_id | RESTRICT | 배송 이력 보존 |
| customers → happy_calls | happy_calls.customer_id | RESTRICT | 해피콜 이력 보존 |
| leads → consultations | consultations.lead_id | SET NULL | 리드 삭제 시 상담 기록 보존 |
| consultations → contracts | contracts.consultation_id | SET NULL | 상담 삭제 시 계약 보존 |
| contracts → deliveries | deliveries.contract_id | RESTRICT | 계약 삭제 전 배송 처리 필요 |
| purchase_requests → purchase_request_items | purchase_request_items.purchase_request_id | CASCADE | 발주요청 삭제 시 품목도 삭제 |
| purchase_requests → purchase_orders | purchase_orders.purchase_request_id | SET NULL | 발주요청 삭제 시 발주서 보존 |
| purchase_orders → purchase_order_items | purchase_order_items.purchase_order_id | CASCADE | 발주서 삭제 시 품목도 삭제 |
| purchase_orders → invoices | invoices.purchase_order_id | RESTRICT | 인보이스가 있는 발주서 삭제 방지 |
| purchase_orders → shipments | shipments.purchase_order_id | RESTRICT | 선적이 있는 발주서 삭제 방지 |
| deliveries → happy_calls | happy_calls.delivery_id | RESTRICT | 해피콜이 있는 배송 삭제 방지 |
| users → contracts | contracts.created_by | SET NULL | 계약 기록 보존 |
| users → purchase_requests | purchase_requests.created_by | SET NULL | 발주요청 기록 보존 |
| users → purchase_orders | purchase_orders.created_by | SET NULL | 발주서 기록 보존 |
| users → consultations | consultations.assigned_to | SET NULL | 상담 기록 보존 |
| users → happy_calls | happy_calls.assigned_to | SET NULL | 해피콜 기록 보존 |
| users → attachments | attachments.uploaded_by | SET NULL | 첨부파일 기록 보존 |

### 5-2. 소프트 삭제 적용 테이블

소프트 삭제(deleted_at IS NOT NULL)를 사용하는 테이블은 물리적 DELETE 대신 deleted_at 업데이트로 처리한다. 모든 조회 쿼리에 `WHERE deleted_at IS NULL` 조건 필수.

| 테이블 | 소프트 삭제 적용 |
|--------|-----------------|
| users | ✅ |
| projects | ✅ |
| products | ✅ |
| customers | ✅ |
| leads | ✅ |
| contracts | ✅ |
| project_sites | ❌ (is_enabled 토글로 대체) |
| event_logs | ❌ (append-only, 삭제 불가) |
| admin_actions | ❌ (감사 로그, 삭제 불가) |
| error_reports | ❌ (오류 기록, 삭제 불가) |
| capacity_slots | ❌ (slot_status=closed로 대체) |

### 5-3. 순환 참조 방지

```
issue_groups.github_issue_id → github_issues (nullable)
github_issues.issue_group_id → issue_groups

위 양방향 참조는 순환 참조 위험이 있음.
해결: issue_groups.github_issue_id는 애플리케이션 레이어에서만 관리.
     DB FK는 github_issues.issue_group_id → issue_groups 단방향만 설정.
     issue_groups.github_issue_id는 FK 없이 UUID 컬럼으로만 유지.
```

---

*최종 업데이트: 2026-03-12*
