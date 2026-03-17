# Research: 나인탁 발주서 엑셀 업로드 → 자동 파싱 기능

## 1. 현재 상태

| 항목 | 상태 |
|------|------|
| 발주서 API (CRUD) | ✅ 완성 |
| 발주서 UI (수동 입력) | ✅ 완성 |
| API items[] 배열 지원 | ✅ 지원 |
| 파일 업로드 인프라 (Presigned URL) | ✅ Mock |
| **엑셀 파싱 로직** | ❌ 없음 |
| **나인탁 발주서 포맷 정의** | ❌ 없음 |

## 2. 기존 아키텍처

### 백엔드 계층
```
Router (purchase_orders.py)
  ↓
Service (purchase_order_service.py)
  ↓
Model (purchase_order.py → PurchaseOrder + PurchaseOrderItem)
  ↓
PostgreSQL
```

### PurchaseOrder 모델
```
id, order_number, supplier_name, order_date, currency, total_amount,
payment_status, order_status, created_by, idempotency_key
```

### PurchaseOrderItem 모델
```
id, order_id(FK), product_id(FK→products), ordered_qty, unit_price, line_total
```

### Product 모델
```
id, brand_name, product_code(unique), product_name, category_name,
unit_price, currency, supplier_name
```

### 기존 API 엔드포인트
- `POST /api/v1/arki/purchase-orders` — items[] 배열 포함 생성 지원
- `POST /api/v1/files/presign` — Presigned URL 발급 (Mock)

### 프론트엔드 API
```ts
purchaseOrdersApi.create(data, idempotencyKey)
filesApi.presign({ file_name, file_type, related_table })
```

## 3. 누락된 것

### 백엔드
- **openpyxl** 라이브러리 (엑셀 파싱용)
- 엑셀 파서 서비스 (`excel_parser_service.py`)
- 업로드 → 파싱 → 발주서 생성 엔드포인트

### 프론트엔드
- 파일 업로드 UI (드래그앤드롭 / 선택)
- 파싱 결과 프리뷰 테이블
- 오류 항목 표시

## 4. 나인탁 발주서 엑셀 포맷 (추정 — 확인 필요)

나인탁 발주서 엑셀 샘플이 없으므로, 일반적인 발주서 엑셀 포맷 가정:
- 상품코드 / 상품명 / 수량 / 단가 / 금액
- 공급업체명, 발주일, 납기일 등 헤더 영역

**⚠️ 사용자에게 나인탁 발주서 엑셀 샘플 확인 필요**

## 결론

- 기존 API가 items[] 배열을 이미 지원 → 백엔드 생성 로직은 재사용 가능
- 엑셀 파싱 서비스 + 업로드 UI 추가가 핵심
- Presigned URL은 Mock → 직접 업로드(multipart) 방식이 현실적
- 나인탁 발주서 포맷 확인이 우선
