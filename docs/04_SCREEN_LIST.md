# 04 SCREEN LIST — Arkistore Operations Automation System

전체 화면 목록 및 명세. 각 화면의 접근 권한, 주요 기능, 연결 API를 정의한다.

---

## 목차

- [ops-web 화면 목록](#ops-web-화면-목록)
- [arki-web 화면 목록](#arki-web-화면-목록)

---

## ops-web 화면 목록

---

## [OPS-001] 로그인
- **앱**: ops-web
- **경로**: `/login`
- **역할 권한**: 인증 전 접근 (비로그인 상태)
- **주요 기능**:
  - 이메일 + 비밀번호 입력 폼
  - JWT 발급 후 httpOnly 쿠키 저장
  - 로그인 실패 시 에러 메시지 표시
  - 로그인 성공 시 `/ops` 리다이렉트
  - 이미 로그인된 경우 `/ops` 자동 리다이렉트
- **연결 API**:
  - `POST /api/v1/auth/login`

---

## [OPS-010] 운영 대시보드 홈
- **앱**: ops-web
- **경로**: `/ops`
- **역할 권한**: super_admin, ops_admin, support_operator
- **주요 기능**:
  - 전체 프로젝트 수 / 활성 프로젝트 수 KPI 카드
  - 미처리 이슈 그룹 수 (new + grouped + triaged) 요약
  - 최근 오류 신고 목록 (최신 5건)
  - 최근 배포 기록 (최신 5건)
  - 이슈 상태별 분포 차트
  - 빠른 이동 링크 (프로젝트 목록, 이슈 목록, 로그)
- **연결 API**:
  - `GET /api/v1/ops/projects?status=active&limit=5`
  - `GET /api/v1/ops/issues?status=new,grouped,triaged&limit=5`
  - `GET /api/v1/ops/error-reports?limit=5&sort=occurred_at:desc`
  - `GET /api/v1/ops/deployments?limit=5&sort=deployed_at:desc`

---

## [OPS-020] 프로젝트 목록
- **앱**: ops-web
- **경로**: `/ops/projects`
- **역할 권한**: super_admin, ops_admin, support_operator
- **주요 기능**:
  - 프로젝트 목록 테이블 (project_code, name, client_name, status, operation_mode)
  - 상태 필터 (active / maintenance / inactive / archived)
  - 운영 모드 필터 (normal / readonly / emergency)
  - 검색 (프로젝트명, 클라이언트명, project_code)
  - 페이지네이션
  - 프로젝트 등록 버튼 → OPS-021 이동 (super_admin, ops_admin만 표시)
  - 행 클릭 → OPS-022 이동
- **연결 API**:
  - `GET /api/v1/ops/projects`

---

## [OPS-021] 프로젝트 등록
- **앱**: ops-web
- **경로**: `/ops/projects/new`
- **역할 권한**: super_admin, ops_admin
- **주요 기능**:
  - 프로젝트 기본 정보 입력 폼 (project_code, name, client_name, service_type, main_url)
  - 초기 상태 선택 (active / maintenance / inactive)
  - 운영 모드 선택 (normal / readonly / emergency)
  - 저장 후 OPS-022 (프로젝트 상세)로 이동
  - 취소 시 OPS-020으로 복귀
- **연결 API**:
  - `POST /api/v1/ops/projects`

---

## [OPS-022] 프로젝트 상세
- **앱**: ops-web
- **경로**: `/ops/projects/[id]`
- **역할 권한**: super_admin, ops_admin, support_operator
- **주요 기능**:
  - 프로젝트 기본 정보 표시 및 수정 (super_admin, ops_admin)
  - 운영 모드 변경 (super_admin, ops_admin)
  - 프로젝트 상태 변경 (super_admin, ops_admin)
  - 사이트 목록 탭: 등록된 project_sites 목록 표시
  - 사이트 추가 폼 (site_code, site_name, site_url, site_type, is_enabled)
  - 사이트 활성/비활성 토글
  - 해당 프로젝트의 최근 오류 신고 목록 (최신 10건)
  - 해당 프로젝트의 최근 배포 기록 (최신 5건)
- **연결 API**:
  - `GET /api/v1/ops/projects/{id}`
  - `PATCH /api/v1/ops/projects/{id}`
  - `GET /api/v1/ops/projects/{id}/sites`
  - `POST /api/v1/ops/projects/{id}/sites`
  - `PATCH /api/v1/ops/projects/{id}/sites/{site_id}`
  - `GET /api/v1/ops/error-reports?project_id={id}&limit=10`
  - `GET /api/v1/ops/deployments?project_id={id}&limit=5`

---

## [OPS-030] 이슈 그룹 목록
- **앱**: ops-web
- **경로**: `/ops/issues`
- **역할 권한**: super_admin, ops_admin, support_operator
- **주요 기능**:
  - 이슈 그룹 목록 테이블 (group_key, group_title, occurrence_count, first_seen_at, last_seen_at, group_status)
  - 상태 필터 (new / grouped / triaged / github_created / resolved / ignored)
  - 프로젝트 필터 (project_code 기준)
  - 검색 (group_title, error_code)
  - 이슈 그룹 상태 일괄 변경 (super_admin, ops_admin, support_operator)
  - GitHub 이슈 생성 버튼 (triaged 상태 그룹 대상, super_admin, ops_admin, support_operator)
  - 이슈 그룹 클릭 시 연결된 error_reports 목록 드로어/모달 표시
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/ops/issues`
  - `PATCH /api/v1/ops/issues/{group_id}/status`
  - `POST /api/v1/ops/issues/{group_id}/github`

---

## [OPS-040] 이벤트/오류 로그
- **앱**: ops-web
- **경로**: `/ops/logs`
- **역할 권한**: super_admin, ops_admin, support_operator
- **주요 기능**:
  - 탭 전환: 이벤트 로그 / 오류 신고 목록
  - **이벤트 로그 탭**:
    - 로그 목록 테이블 (project_code, environment, event_type, event_name, logged_at)
    - 프로젝트 필터, 환경 필터, 이벤트 타입 필터
    - 날짜 범위 필터
    - payload JSONB 상세 보기 (행 클릭 시 모달)
  - **오류 신고 탭**:
    - 오류 신고 목록 (project_code, site_type, error_code, error_message_masked, report_status, occurred_at)
    - 상태 필터, 프로젝트 필터, 환경 필터
    - 날짜 범위 필터
    - 이슈 그룹 연결 여부 표시
    - 신고 상세 보기 (행 클릭 시 모달)
  - 페이지네이션 (각 탭 독립)
- **연결 API**:
  - `GET /api/v1/ops/logs/events`
  - `GET /api/v1/ops/error-reports`

---

## [OPS-050] 배포 기록
- **앱**: ops-web
- **경로**: `/ops/deployments`
- **역할 권한**: super_admin, ops_admin, support_operator
- **주요 기능**:
  - 배포 기록 목록 테이블 (project, site, environment, version_tag, deployed_by, deployed_at, status)
  - 프로젝트 필터, 환경 필터, 상태 필터 (success / failed)
  - 날짜 범위 필터
  - 배포 노트 상세 보기 (행 클릭 시 모달)
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/ops/deployments`

---

## arki-web 화면 목록

---

## [ARKI-001] 로그인
- **앱**: arki-web
- **경로**: `/login`
- **역할 권한**: 인증 전 접근 (비로그인 상태)
- **주요 기능**:
  - 이메일 + 비밀번호 입력 폼
  - JWT 발급 후 httpOnly 쿠키 저장
  - 로그인 실패 시 에러 메시지 표시
  - 로그인 성공 시 `/arki/dashboard` 리다이렉트
  - 이미 로그인된 경우 `/arki/dashboard` 자동 리다이렉트
- **연결 API**:
  - `POST /api/v1/auth/login`

---

## [ARKI-010] 메인 대시보드
- **앱**: arki-web
- **경로**: `/arki/dashboard`
- **역할 권한**: super_admin, arki_logistics, arki_sales, arki_store_manager
- **주요 기능**:
  - KPI 카드 6종:
    - 발주 대기 건수 (purchase_requests.status = requested)
    - 재고 부족 상품 수 (inventories.inventory_status = low_stock 또는 out_of_stock)
    - 신규 문의 건수 (leads.status = new)
    - 오늘 배송 건수 (deliveries.delivery_date = today)
    - CAPA 잔여율 (오늘 날짜 capacity_slots 평균 remaining/max)
    - 미처리 오류 신고 건수 (error_reports.report_status = new)
  - 역할별 KPI 노출 제어 (arki_logistics: 발주/재고/CAPA, arki_sales: 신규문의, arki_store_manager: 오늘배송/해피콜)
  - 최근 활동 피드 (최신 10건 admin_actions)
- **연결 API**:
  - `GET /api/v1/arki/dashboard/summary`

---

## [ARKI-020] 상품 목록
- **앱**: arki-web
- **경로**: `/arki/products`
- **역할 권한**: super_admin, arki_logistics
- **주요 기능**:
  - 상품 목록 테이블 (brand_name, product_code, product_name, category_name, unit_price, currency, supplier_name, is_active)
  - 활성/비활성 필터
  - 브랜드명, 카테고리 필터
  - 검색 (product_code, product_name, supplier_name)
  - 상품 등록 버튼 → ARKI-021 이동
  - 행 클릭 시 상품 상세/수정 슬라이드 패널
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/arki/products`

---

## [ARKI-021] 상품 등록
- **앱**: arki-web
- **경로**: `/arki/products/new`
- **역할 권한**: super_admin, arki_logistics
- **주요 기능**:
  - 상품 정보 입력 폼 (brand_name, product_code, product_name, category_name, option_text, unit_price, currency, supplier_name)
  - is_active 초기값 true
  - 저장 후 ARKI-020 목록으로 이동
  - 취소 시 ARKI-020으로 복귀
- **연결 API**:
  - `POST /api/v1/arki/products`

---

## [ARKI-030] 재고 현황
- **앱**: arki-web
- **경로**: `/arki/inventory`
- **역할 권한**: super_admin, arki_logistics
- **주요 기능**:
  - 재고 목록 테이블 (product_code, product_name, warehouse_name, current_stock, reserved_stock, available_stock, safety_stock, inventory_status)
  - 재고 상태 필터 (normal / low_stock / out_of_stock / overstock)
  - 창고명 필터
  - 검색 (product_code, product_name)
  - 재고 수동 조정 버튼 (행별): 수량 직접 입력 모달
  - 입고 예정일 표시 (expected_inbound_date)
  - 재고 부족 상품 상단 정렬 옵션
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/arki/inventory`
  - `PATCH /api/v1/arki/inventory/{id}`

---

## [ARKI-040] 발주 요청 목록
- **앱**: arki-web
- **경로**: `/arki/purchase-requests`
- **역할 권한**: super_admin, arki_logistics
- **주요 기능**:
  - 발주 요청 목록 테이블 (요청번호, 상품명, 요청수량, 요청자, 상태, 생성일)
  - 상태 필터 (requested / reviewed / approved / rejected / converted_to_order)
  - 날짜 범위 필터
  - 검색 (상품명, 요청번호)
  - 상태 변경 버튼 (reviewed → approved / rejected, 사유 입력 모달)
  - 발주 요청 등록 버튼 → ARKI-041 이동
  - 행 클릭 시 상세 슬라이드 패널 (품목 목록 포함)
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/arki/purchase-requests`
  - `PATCH /api/v1/arki/purchase-requests/{id}/status`

---

## [ARKI-041] 발주 요청 등록
- **앱**: arki-web
- **경로**: `/arki/purchase-requests/new`
- **역할 권한**: super_admin, arki_logistics
- **주요 기능**:
  - 발주 요청 헤더 정보 입력 (공급사명, 요청 사유, 희망 납기일)
  - 품목 동적 추가/삭제 (product_id 선택, 요청수량, 단가, 비고)
  - 상품 검색 팝업 (product_code / product_name 검색)
  - 총 금액 자동 계산
  - 저장 시 Idempotency-Key 자동 생성 (중복 제출 방지)
  - 저장 후 ARKI-040 목록으로 이동
- **연결 API**:
  - `POST /api/v1/arki/purchase-requests` (Idempotency-Key 헤더 필수)
  - `GET /api/v1/arki/products?is_active=true` (상품 검색용)

---

## [ARKI-050] 발주서 목록
- **앱**: arki-web
- **경로**: `/arki/purchase-orders`
- **역할 권한**: super_admin, arki_logistics
- **주요 기능**:
  - 발주서 목록 테이블 (발주서번호, 공급사, 발주일, 총금액, 상태, 연결 발주요청)
  - 상태 필터 (created / ordered / invoiced / shipped / completed / cancelled)
  - 날짜 범위 필터
  - 검색 (발주서번호, 공급사명)
  - 상태 변경 버튼 (단계별 전이, 취소 시 사유 입력 모달)
  - 발주서 등록 버튼 → ARKI-051 이동
  - 행 클릭 시 상세 슬라이드 패널 (품목 목록, 연결 인보이스/선적 정보)
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/arki/purchase-orders`
  - `PATCH /api/v1/arki/purchase-orders/{id}/status`

---

## [ARKI-051] 발주서 등록
- **앱**: arki-web
- **경로**: `/arki/purchase-orders/new`
- **역할 권한**: super_admin, arki_logistics
- **주요 기능**:
  - 발주서 헤더 정보 입력 (공급사명, 발주일, 납기 예정일, 통화, 비고)
  - 연결 발주 요청 선택 (선택 시 품목 자동 채움)
  - 품목 동적 추가/삭제 (product_id, 수량, 단가, 소계)
  - 총 금액 자동 계산
  - 저장 시 Idempotency-Key 자동 생성
  - 저장 후 ARKI-050 목록으로 이동
- **연결 API**:
  - `POST /api/v1/arki/purchase-orders` (Idempotency-Key 헤더 필수)
  - `GET /api/v1/arki/purchase-requests?status=approved` (연결 발주요청 선택용)

---

## [ARKI-060] 인보이스 목록
- **앱**: arki-web
- **경로**: `/arki/invoices`
- **역할 권한**: super_admin, arki_logistics
- **주요 기능**:
  - 인보이스 목록 테이블 (인보이스번호, 연결 발주서, 공급사, 인보이스일, 금액, 통화)
  - 날짜 범위 필터
  - 검색 (인보이스번호, 발주서번호)
  - 인보이스 등록 버튼 (모달 또는 슬라이드 패널)
  - 첨부 파일 다운로드 링크
  - 행 클릭 시 상세 보기 모달
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/arki/invoices`
  - `POST /api/v1/arki/invoices`

---

## [ARKI-070] 선적 목록
- **앱**: arki-web
- **경로**: `/arki/shipments`
- **역할 권한**: super_admin, arki_logistics
- **주요 기능**:
  - 선적(BL) 목록 테이블 (BL번호, 연결 발주서, 선사, ETD, ETA, 상태)
  - 상태 필터 (pending / in_transit / arrived / completed)
  - 날짜 범위 필터 (ETD / ETA 기준)
  - 검색 (BL번호, 발주서번호)
  - BL 등록 버튼 (모달 또는 슬라이드 패널)
  - 상태 변경 버튼
  - 첨부 파일 (BL 스캔본) 업로드/다운로드
  - 행 클릭 시 상세 보기 모달
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/arki/shipments`
  - `POST /api/v1/arki/shipments`
  - `PATCH /api/v1/arki/shipments/{id}`

---

## [ARKI-080] 고객 목록
- **앱**: arki-web
- **경로**: `/arki/customers`
- **역할 권한**: super_admin, arki_sales, arki_store_manager
- **주요 기능**:
  - 고객 목록 테이블 (name, phone_masked, email_masked, customer_type, grade, is_vip, region, source_channel)
  - 고객 유형 필터 (individual / business)
  - 등급 필터 (CustomerGrade enum)
  - VIP 필터
  - 검색 (name, phone_masked, email_masked)
  - 고객 등록 버튼 → ARKI-081 이동
  - 행 클릭 시 고객 상세 슬라이드 패널 (계약 이력, 상담 이력, 리드 이력)
  - VIP 등급 변경 버튼 (arki_sales, super_admin만)
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/arki/customers`
  - `PATCH /api/v1/arki/customers/{id}` (VIP 등급 변경)

---

## [ARKI-081] 고객 등록
- **앱**: arki-web
- **경로**: `/arki/customers/new`
- **역할 권한**: super_admin, arki_sales, arki_store_manager
- **주요 기능**:
  - 고객 정보 입력 폼 (customer_type, name, phone, email, region, source_channel)
  - 등급 초기값 설정 (CustomerGrade 선택)
  - is_vip 체크박스 (arki_sales, super_admin만 활성화)
  - 저장 후 ARKI-080 목록으로 이동
  - 취소 시 ARKI-080으로 복귀
- **연결 API**:
  - `POST /api/v1/arki/customers`

---

## [ARKI-090] 리드 목록
- **앱**: arki-web
- **경로**: `/arki/leads`
- **역할 권한**: super_admin, arki_sales
- **주요 기능**:
  - 리드 목록 테이블 (고객명, 연락처_masked, 유입경로, 관심상품, 상태, 생성일)
  - 상태 필터 (new / in_progress / converted / closed / dropped)
  - 유입경로 필터
  - 날짜 범위 필터
  - 검색 (고객명, 연락처)
  - 리드 등록 버튼 → ARKI-091 이동
  - 행 클릭 시 상세 슬라이드 패널 (상담 이력 연결)
  - 상태 변경 버튼 (전이 규칙 준수)
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/arki/leads`
  - `PATCH /api/v1/arki/leads/{id}/status`

---

## [ARKI-091] 리드 등록
- **앱**: arki-web
- **경로**: `/arki/leads/new`
- **역할 권한**: super_admin, arki_sales
- **주요 기능**:
  - 리드 정보 입력 폼 (고객 선택 또는 신규 고객 정보 입력, 유입경로, 관심상품, 메모)
  - 기존 고객 검색 연결 (customer_id 선택)
  - 초기 상태 자동 설정 (new)
  - 저장 후 ARKI-090 목록으로 이동
- **연결 API**:
  - `POST /api/v1/arki/leads`
  - `GET /api/v1/arki/customers?limit=20` (고객 검색용)

---

## [ARKI-100] 상담 목록
- **앱**: arki-web
- **경로**: `/arki/consultations`
- **역할 권한**: super_admin, arki_sales, arki_store_manager
- **주요 기능**:
  - 상담 목록 테이블 (고객명, 상담일시, 상담유형, 담당자, 결과, 계약 연결 여부)
  - 상담 유형 필터
  - 날짜 범위 필터
  - 담당자 필터
  - 검색 (고객명)
  - 상담 등록 버튼 → ARKI-101 이동
  - 행 클릭 시 상세 보기 모달 (상담 내용, 연결 계약)
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/arki/consultations`

---

## [ARKI-101] 상담 등록
- **앱**: arki-web
- **경로**: `/arki/consultations/new`
- **역할 권한**: super_admin, arki_sales, arki_store_manager
- **주요 기능**:
  - 상담 정보 입력 폼 (고객 선택, 리드 연결 선택, 상담일시, 상담유형, 상담내용, 결과, 다음 액션)
  - 기존 고객 검색 연결 (customer_id 필수)
  - 리드 연결 선택 (lead_id 선택, 선택 시 리드 정보 자동 표시)
  - 저장 후 ARKI-100 목록으로 이동
- **연결 API**:
  - `POST /api/v1/arki/consultations`
  - `GET /api/v1/arki/customers?limit=20` (고객 검색용)
  - `GET /api/v1/arki/leads?customer_id={id}` (리드 연결용)

---

## [ARKI-110] 계약 목록
- **앱**: arki-web
- **경로**: `/arki/contracts`
- **역할 권한**: super_admin, arki_store_manager
- **주요 기능**:
  - 계약 목록 테이블 (contract_number, 고객명, 계약일, 계약금액, 입금액, 상태, 배송필요여부)
  - 상태 필터 (draft / signed / confirmed / cancelled)
  - 날짜 범위 필터
  - 검색 (contract_number, 고객명)
  - 계약 생성 버튼 → ARKI-111 이동
  - 행 클릭 시 계약 상세 슬라이드 패널 (첨부파일, 배송 연결 정보)
  - 상태 변경 버튼 (전이 규칙 준수, cancelled 시 메모 필수)
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/arki/contracts`
  - `PATCH /api/v1/arki/contracts/{id}/status`

---

## [ARKI-111] 계약 생성
- **앱**: arki-web
- **경로**: `/arki/contracts/new`
- **역할 권한**: super_admin, arki_store_manager
- **주요 기능**:
  - 계약 정보 입력 폼 (고객 선택, 상담 연결 선택, 계약일, 계약금액, 입금액, 배송필요여부, 비고)
  - 기존 고객 검색 연결 (customer_id 필수)
  - 상담 연결 선택 (consultation_id 선택)
  - 초기 상태 자동 설정 (draft)
  - 첨부파일 업로드 (계약서 PDF)
  - 저장 시 Idempotency-Key 자동 생성 (중복 제출 방지)
  - 저장 후 ARKI-110 목록으로 이동
- **연결 API**:
  - `POST /api/v1/arki/contracts` (Idempotency-Key 헤더 필수)
  - `GET /api/v1/arki/customers?limit=20` (고객 검색용)
  - `GET /api/v1/arki/consultations?customer_id={id}` (상담 연결용)
  - `POST /api/v1/files/presign` (첨부파일 업로드)

---

## [ARKI-120] 배송 목록
- **앱**: arki-web
- **경로**: `/arki/deliveries`
- **역할 권한**: super_admin, arki_logistics, arki_store_manager
- **주요 기능**:
  - 배송 목록 테이블 (delivery_number, 고객명, 배송일, 시간대, 배송팀, 주소, 상태, 사다리차여부)
  - 상태 필터 (scheduled / confirmed / in_transit / completed / cancelled / delayed)
  - 날짜 필터 (delivery_date 기준)
  - 배송팀 필터
  - 검색 (delivery_number, 고객명, 주소)
  - 배송 예약 버튼 → ARKI-121 이동
  - 행 클릭 시 배송 상세 슬라이드 패널 (연결 계약, 해피콜 이력)
  - 상태 변경 버튼 (전이 규칙 준수, 지연/취소 시 사유 필수)
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/arki/deliveries`
  - `PATCH /api/v1/arki/deliveries/{id}/status`

---

## [ARKI-121] 배송 예약
- **앱**: arki-web
- **경로**: `/arki/deliveries/new`
- **역할 권한**: super_admin, arki_store_manager
- **주요 기능**:
  - 배송 정보 입력 폼 (계약 선택, 고객 자동 채움, 배송일, 시간대, 배송팀, 차량코드, 주소, 사다리차여부)
  - 계약 선택 시 고객 정보 자동 채움
  - 배송일 + 시간대 선택 시 CAPA 잔여 실시간 표시
  - CAPA 초과 시 경고 표시 (저장은 가능하나 경고)
  - 저장 시 Idempotency-Key 자동 생성
  - 저장 후 ARKI-120 목록으로 이동
- **연결 API**:
  - `POST /api/v1/arki/deliveries` (Idempotency-Key 헤더 필수)
  - `GET /api/v1/arki/contracts?status=confirmed` (계약 선택용)
  - `GET /api/v1/arki/capacity-slots?slot_date={date}` (CAPA 조회용)

---

## [ARKI-130] 배송 CAPA
- **앱**: arki-web
- **경로**: `/arki/capacity-slots`
- **역할 권한**: super_admin, arki_logistics
- **주요 기능**:
  - 캘린더 뷰 + 테이블 뷰 전환
  - 날짜별 / 배송팀별 / 시간대별 CAPA 현황 (max_capacity, used_capacity, remaining_capacity, slot_status)
  - 슬롯 상태 색상 표시 (open: 초록, limited: 노랑, full: 빨강, closed: 회색)
  - CAPA 슬롯 등록 버튼 (모달): slot_date, delivery_team, time_slot, max_capacity 입력
  - 슬롯 수정 버튼 (max_capacity, slot_status 변경)
  - 날짜 범위 필터
  - 배송팀 필터
- **연결 API**:
  - `GET /api/v1/arki/capacity-slots`
  - `POST /api/v1/arki/capacity-slots`
  - `PATCH /api/v1/arki/capacity-slots/{id}`

---

## [ARKI-140] 해피콜 목록
- **앱**: arki-web
- **경로**: `/arki/happy-calls`
- **역할 권한**: super_admin, arki_store_manager
- **주요 기능**:
  - 해피콜 목록 테이블 (고객명, 연결 배송, 배송일, 해피콜 유형, 결과, 담당자, 등록일)
  - 해피콜 유형 필터 (pre_delivery / post_delivery)
  - 결과 필터 (success / no_answer / rescheduled / cancelled)
  - 날짜 범위 필터
  - 검색 (고객명, 배송번호)
  - 해피콜 등록 버튼 → ARKI-141 이동
  - 행 클릭 시 상세 보기 모달 (통화 내용, 연결 배송 정보)
  - 페이지네이션
- **연결 API**:
  - `GET /api/v1/arki/happy-calls`

---

## [ARKI-141] 해피콜 등록
- **앱**: arki-web
- **경로**: `/arki/happy-calls/new`
- **역할 권한**: super_admin, arki_store_manager
- **주요 기능**:
  - 해피콜 정보 입력 폼 (배송 선택, 고객 자동 채움, 해피콜 유형, 통화일시, 결과, 통화 내용, 다음 액션)
  - 배송 선택 시 고객 정보 자동 채움
  - 결과가 rescheduled인 경우 재예약 일시 입력 필드 표시
  - 저장 후 ARKI-140 목록으로 이동
- **연결 API**:
  - `POST /api/v1/arki/happy-calls`
  - `GET /api/v1/arki/deliveries?status=scheduled,confirmed` (배송 선택용)

---

*최종 업데이트: 2026-03-12*
