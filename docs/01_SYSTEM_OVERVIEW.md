# 01 SYSTEM OVERVIEW — Arkistore Operations Automation System

## 1. 시스템 구성

### 1-1. 논리 구조

```
┌─────────────────────────────────────────────────────┐
│         JH Customer Management Solution              │
│              (운영관리 대시보드)                       │
│  프로젝트관리 | 오류/로그/이슈 | 배포 | 운영모드 | 권한  │
└──────────────────────┬──────────────────────────────┘
                       │ 상위 운영관제
┌──────────────────────▼──────────────────────────────┐
│                Arkistore System                      │
│  ┌───────────┐ ┌──────────┐ ┌─────────┐ ┌────────┐ │
│  │  메인대시  │ │  물류    │ │  영업   │ │판매매니│ │
│  │  보드    │ │  사이트  │ │  사이트 │ │저 사이트│ │
│  └───────────┘ └──────────┘ └─────────┘ └────────┘ │
└─────────────────────────────────────────────────────┘
```

### 1-2. 앱 구성

| 앱 | 경로 | 역할 |
|----|------|------|
| ops-web | apps/ops-web | JH 운영관리 대시보드 (Next.js) |
| arki-web | apps/arki-web | Arkistore 업무 시스템 (Next.js) |
| api | apps/api | 공통 FastAPI 백엔드 |

---

## 2. 도메인 분리 원칙

### 2-1. Arkistore 업무 도메인 (현업 실무)

```
products          상품 마스터
inventory         재고 관리
customers         고객 관리
leads             문의/리드
consultations     상담 기록
contracts         계약 관리
purchase_requests 발주 요청
purchase_orders   발주서
invoices          인보이스
shipments         BL/선적
deliveries        배송 예약
capacity_slots    배송 CAPA
happy_calls       해피콜
attachments       첨부 파일
```

### 2-2. JH Ops 운영 도메인 (운영/관제)

```
projects           프로젝트 등록
project_sites      사이트 등록
error_reports      오류 신고
issue_groups       오류 그룹
github_issues      GitHub 이슈
event_logs         이벤트 로그
admin_actions      관리자 감사로그
deployment_records 배포 기록
sheet_sync_jobs    시트 동기화 작업
```

---

## 3. 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | Next.js 14+ (App Router) |
| Backend | FastAPI 0.110+ |
| DB | PostgreSQL 15+ |
| ORM | SQLAlchemy 2.x |
| Migration | Alembic |
| Schema | Pydantic v2 |
| Auth | JWT (httpOnly cookie) |
| File | Google Drive / S3-compatible |
| Issue | GitHub Issues API |
| Sheets | Google Sheets API v4 |
| Task Queue | Celery (Phase 2 이후) |
| Cache | Redis (Phase 2 이후) |

---

## 4. API 구조

```
/api/v1/auth/*            인증
/api/v1/ops/projects/*    프로젝트 관리
/api/v1/ops/issues/*      오류/이슈 관리
/api/v1/ops/logs/*        로그 관리
/api/v1/arki/dashboard/*  대시보드
/api/v1/arki/products/*   상품
/api/v1/arki/inventory/*  재고
/api/v1/arki/customers/*  고객
/api/v1/arki/leads/*      문의/리드
/api/v1/arki/consultations/* 상담
/api/v1/arki/contracts/*  계약
/api/v1/arki/purchase-requests/* 발주 요청
/api/v1/arki/purchase-orders/*   발주서
/api/v1/arki/invoices/*   인보이스
/api/v1/arki/shipments/*  선적
/api/v1/arki/deliveries/* 배송
/api/v1/arki/capacity-slots/* CAPA
/api/v1/arki/happy-calls/* 해피콜
/api/v1/files/*           파일
/api/v1/sync/*            동기화
/api/v1/ops/error-reports/* 오류 신고
```

---

## 5. 외부 연동

| 시스템 | 방식 | 상태 |
|--------|------|------|
| Ecount | Adapter + Mock-first | Phase 6 |
| Nine United 포털 | Adapter + Mock-first | Phase 6 |
| UNI-PASS 통관 | Adapter + Mock-first | Phase 6 |
| GitHub Issues | REST API v3 | Phase 5 |
| Google Sheets | Sheets API v4 | Phase 6 |
| Google Drive | Drive API v3 | Phase 1 (presign only) |
| S3-compatible Storage | Presigned URL | Phase 1 |

---

## 6. 역할 구분 (초기 MVP)

| 역할 | 설명 |
|------|------|
| super_admin | 전체 시스템 관리 |
| ops_admin | JH 운영대시보드 전체 관리 |
| arki_logistics | Arkistore 물류 담당 |
| arki_sales | Arkistore 영업 담당 |
| arki_store_manager | Arkistore 판매매니저 |
| support_operator | 오류 조회/지원 |

---

*최종 업데이트: 2026-03-11*
