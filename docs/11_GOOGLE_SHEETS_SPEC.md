# 11 GOOGLE SHEETS SPEC — 시트 명세

## 원칙

> Google Sheets는 **보조 운영 레이어**입니다.
> PostgreSQL이 원본 DB이며, Sheets는 조회/보고용입니다.

---

## 1. Export 대상 시트

| 시트명 | 원본 테이블 | 용도 | 트리거 |
|--------|------------|------|--------|
| 발주요청현황 | purchase_requests + items | 발주 검토 | 수동/주기 |
| 발주서현황 | purchase_orders + items | 발주 추적 | 수동/주기 |
| 재고현황 | inventories + products | 재고 모니터링 | 수동/주기 |
| 계약현황 | contracts + customers | 영업 현황 | 수동/주기 |
| 배송스케줄 | deliveries + customers | 배송 계획 | 수동/일별 |
| 고객목록 | customers | CRM | 수동 |
| 오류리포트 | error_reports + issue_groups | 이슈 현황 | 수동 |

---

## 2. 시트 컬럼 정의

### 발주요청현황

| 컬럼 | 원본 필드 | 비고 |
|------|----------|------|
| 요청번호 | request_number | |
| 요청일 | created_at | |
| 요청자 | created_by → users.name | |
| 상태 | request_status | 한글 변환 |
| 필요일 | required_date | |
| 상품코드 | items → product.product_code | |
| 상품명 | items → product.product_name | |
| 요청수량 | items → requested_qty | |
| 요청사유 | reason_text | |

### 발주서현황

| 컬럼 | 원본 필드 | 비고 |
|------|----------|------|
| 발주서번호 | order_number | |
| 발주일 | order_date | |
| 공급사 | supplier_name | |
| 통화 | currency | |
| 합계금액 | total_amount | |
| 결제상태 | payment_status | 한글 변환 |
| 발주상태 | order_status | 한글 변환 |
| 상품코드 | items → product.product_code | |
| 발주수량 | items → ordered_qty | |
| 단가 | items → unit_price | |
| 소계 | items → line_total | |

### 배송스케줄

| 컬럼 | 원본 필드 | 비고 |
|------|----------|------|
| 배송번호 | delivery_number | |
| 배송일 | delivery_date | |
| 시간대 | time_slot | |
| 팀 | delivery_team | |
| 고객명 | customer → name | |
| 주소 | address_text | |
| 사다리여부 | ladder_required | Y/N |
| 상태 | delivery_status | 한글 변환 |
| 계약번호 | contract → contract_number | |
| 해피콜완료 | happy_call → call_result | |

---

## 3. 역반영(Sheets → DB) 허용 범위

> ⚠️ 기본적으로 **단방향(DB → Sheets)**만 허용

예외적으로 역반영 허용 범위:
- **없음 (MVP 기준)**
- Phase 2 이후 검토: 수량 조정, 특이사항 메모

---

## 4. 동기화 방식

| 방식 | 설명 |
|------|------|
| 수동 Export | 관리자가 버튼 클릭 → `/sync/sheets/export` API 호출 |
| 주기적 Export | Celery beat (Phase 2 이후) |
| 웹훅 | 미지원 (MVP) |

---

## 5. 실패 처리

- Export 실패 시: `sheet_sync_jobs.job_status = 'failed'` + `error_message` 기록
- 부분 실패: 전체 롤백 후 재시도
- 알림: 관리자 이메일 (Phase 2 이후)

---

## 6. 접근 권한

| 역할 | 시트 접근 |
|------|----------|
| super_admin | 전체 시트 읽기/쓰기 |
| ops_admin | 전체 시트 읽기 |
| arki_logistics | 발주/재고 시트 |
| arki_sales | 고객/계약 시트 |
| arki_store_manager | 배송/계약 시트 |
| support_operator | 없음 |
