# 08 BACKEND STRUCTURE STANDARD — FastAPI

## 1. 계층 책임 원칙

| 계층 | 책임 | 금지 |
|------|------|------|
| api/ | 라우팅, 요청/응답, 권한체크 | 비즈니스 로직, DB 직접 접근 |
| services/ | 비즈니스 로직, 상태전이, 외부연동 조합 | DB 직접 ORM 조작 |
| repositories/ | DB 접근, CRUD, 필터, 페이지네이션 | 비즈니스 판단 |
| models/ | ORM 테이블 정의 | 비즈니스 로직 |
| schemas/ | Pydantic DTO | DB 접근 |
| integrations/ | 외부 API 호출 래핑 | 비즈니스 판단 |
| core/ | 공통 설정, 인증, 예외, 응답포맷 | 도메인 로직 |

## 2. 폴더 구조

```
apps/api/app/
├─ main.py
├─ api/
│  ├─ deps.py
│  └─ v1/
│     ├─ router.py
│     ├─ auth.py
│     ├─ ops_projects.py
│     ├─ ops_issues.py
│     ├─ ops_logs.py
│     ├─ dashboard.py
│     ├─ products.py
│     ├─ inventory.py
│     ├─ customers.py
│     ├─ leads.py
│     ├─ consultations.py
│     ├─ contracts.py
│     ├─ purchase_requests.py
│     ├─ purchase_orders.py
│     ├─ invoices.py
│     ├─ shipments.py
│     ├─ deliveries.py
│     ├─ capacity_slots.py
│     ├─ happy_calls.py
│     ├─ files.py
│     ├─ sync.py
│     └─ error_reports.py
│
├─ core/
│  ├─ config.py           환경변수 로드
│  ├─ database.py         DB 엔진/세션/의존성
│  ├─ security.py         비밀번호 해시, JWT, 쿠키
│  ├─ permissions.py      역할 기반 접근 제어
│  ├─ logging.py          로깅 설정
│  ├─ exceptions.py       커스텀 예외 클래스
│  ├─ responses.py        공통 응답 envelope
│  ├─ enums.py            전체 Enum 중앙관리
│  ├─ idempotency.py      중복 요청 방지
│  └─ middleware.py       request_id, trace_id, 에러 캡처
│
├─ db/
│  ├─ base.py             모든 모델 import (alembic용)
│  ├─ session.py          SessionLocal 팩토리
│  ├─ migrations/         Alembic 마이그레이션
│  └─ seeds/              초기 데이터
│
├─ models/
│  ├─ user.py
│  ├─ role.py
│  ├─ project.py
│  ├─ project_site.py
│  ├─ product.py
│  ├─ inventory.py
│  ├─ customer.py
│  ├─ lead.py
│  ├─ consultation.py
│  ├─ contract.py
│  ├─ purchase_request.py
│  ├─ purchase_order.py
│  ├─ invoice.py
│  ├─ shipment.py
│  ├─ delivery.py
│  ├─ capacity_slot.py
│  ├─ happy_call.py
│  ├─ attachment.py
│  ├─ error_report.py
│  ├─ issue_group.py
│  ├─ github_issue.py
│  ├─ event_log.py
│  ├─ admin_action.py
│  ├─ deployment_record.py
│  └─ sheet_sync_job.py
│
├─ schemas/
│  ├─ common.py
│  ├─ auth.py
│  ├─ project.py
│  ├─ issue.py
│  ├─ dashboard.py
│  ├─ product.py
│  ├─ inventory.py
│  ├─ customer.py
│  ├─ lead.py
│  ├─ consultation.py
│  ├─ contract.py
│  ├─ purchase_request.py
│  ├─ purchase_order.py
│  ├─ invoice.py
│  ├─ shipment.py
│  ├─ delivery.py
│  ├─ capacity_slot.py
│  ├─ happy_call.py
│  ├─ file.py
│  ├─ sync.py
│  └─ error_report.py
│
├─ repositories/
│  ├─ base.py
│  ├─ user_repository.py
│  ├─ project_repository.py
│  ├─ issue_repository.py
│  ├─ product_repository.py
│  ├─ inventory_repository.py
│  ├─ customer_repository.py
│  ├─ lead_repository.py
│  ├─ consultation_repository.py
│  ├─ contract_repository.py
│  ├─ purchase_request_repository.py
│  ├─ purchase_order_repository.py
│  ├─ invoice_repository.py
│  ├─ shipment_repository.py
│  ├─ delivery_repository.py
│  ├─ capacity_slot_repository.py
│  ├─ happy_call_repository.py
│  ├─ attachment_repository.py
│  ├─ event_log_repository.py
│  └─ sync_job_repository.py
│
├─ services/
│  ├─ auth_service.py
│  ├─ ops/
│  │  ├─ project_service.py
│  │  ├─ issue_service.py
│  │  ├─ log_service.py
│  │  ├─ deployment_service.py
│  │  └─ operation_mode_service.py
│  ├─ arki/
│  │  ├─ dashboard_service.py
│  │  ├─ product_service.py
│  │  ├─ inventory_service.py
│  │  ├─ customer_service.py
│  │  ├─ lead_service.py
│  │  ├─ consultation_service.py
│  │  ├─ contract_service.py
│  │  ├─ purchase_request_service.py
│  │  ├─ purchase_order_service.py
│  │  ├─ invoice_service.py
│  │  ├─ shipment_service.py
│  │  ├─ delivery_service.py
│  │  ├─ capacity_service.py
│  │  └─ happy_call_service.py
│  ├─ file_service.py
│  ├─ sync_service.py
│  ├─ error_report_service.py
│  └─ audit_service.py
│
├─ integrations/
│  ├─ github/
│  │  ├─ client.py        GitHub REST API 래퍼
│  │  └─ adapter.py       이슈 생성/조회 adapter
│  ├─ google/
│  │  ├─ sheets_client.py Google Sheets API 래퍼
│  │  ├─ drive_client.py  Google Drive API 래퍼
│  │  └─ mapper.py        시트 ↔ DB 매핑
│  ├─ storage/
│  │  ├─ s3_client.py     S3 호환 스토리지 클라이언트
│  │  └─ signer.py        Presigned URL 생성
│  └─ agents/
│     ├─ base.py           Agent provider 기본 인터페이스
│     ├─ provider_openai.py
│     ├─ provider_anthropic.py
│     └─ provider_gemini.py
│
├─ tasks/
│  ├─ sync_tasks.py
│  ├─ issue_tasks.py
│  └─ reporting_tasks.py
│
├─ utils/
│  ├─ masking.py           민감정보 마스킹
│  ├─ pagination.py        페이지네이션 헬퍼
│  ├─ datetime.py          날짜 변환 유틸
│  ├─ validators.py        입력값 검증 헬퍼
│  ├─ hashing.py           해시 유틸
│  └─ strings.py           문자열 처리
│
└─ tests/
   ├─ conftest.py
   ├─ api/
   ├─ services/
   └─ repositories/
```

## 3. 상태 전이 원칙

### 계약 (ContractStatus)
```
draft → signed → confirmed
         ↓          ↓
      cancelled  cancelled
```

### 발주 요청 (PurchaseRequestStatus)
```
requested → reviewed → approved → converted_to_order
                    ↓
                 rejected
```

### 발주서 (PurchaseOrderStatus)
```
created → ordered → invoiced → shipped → completed
                                    ↓
                                 cancelled
```

### 배송 (DeliveryStatus)
```
scheduled → confirmed → in_transit → completed
                ↓           ↓
            cancelled    delayed
```

## 4. Idempotency 대상 API

```
POST /arki/contracts
POST /arki/purchase-requests
POST /arki/purchase-orders
POST /arki/deliveries
POST /ops/error-reports
POST /ops/issue-groups/{groupId}/github-issue
POST /sync/sheets/export
```

## 5. 감사로그 대상 액션

```
프로젝트 생성/수정/삭제
운영 모드 변경
이슈 상태 변경
GitHub 이슈 생성
계약 상태 변경
발주 승인/반려
배송 상태 변경
CAPA 수동 수정
시트 동기화 수동 실행
```
