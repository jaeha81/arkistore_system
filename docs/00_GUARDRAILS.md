# 00 GUARDRAILS — Arkistore Operations Automation System

> 이 문서는 **절대 위반하면 안 되는 구현 원칙**입니다.
> Claude Code, 개발 에이전트, 모든 기여자가 반드시 따릅니다.

---

## 시스템 경계 원칙

| 번호 | 원칙 | 설명 |
|------|------|------|
| G-01 | **업무 ↔ 운영 분리** | Arkistore 업무 도메인 코드와 JH Ops 운영 도메인 코드를 절대 합치지 않는다 |
| G-02 | **Sheets는 보조** | Google Sheets는 원본 DB가 아니다. 보조 운영 레이어로만 사용 |
| G-03 | **GitHub은 이슈 허브** | GitHub은 운영 원본 저장소가 아니다. 이슈 추적/배포 허브로만 사용 |
| G-04 | **Adapter-First** | 외부 시스템(Ecount, Nine United, 통관조회)은 반드시 adapter 레이어를 통해 연결 |
| G-05 | **Mock-First** | 검증되지 않은 외부 API는 Mock 구현부터. 실연동은 명시적 승인 후 |
| G-06 | **얇은 라우터** | API 라우터는 요청/응답/권한/스키마 검증만. 비즈니스 로직 금지 |
| G-07 | **서비스 소유** | 비즈니스 로직은 service 계층이 소유. 라우터/모델/리포지토리에 넣지 않는다 |
| G-08 | **Repository 분리** | DB 접근은 repository 계층 전담. 서비스에서 ORM 직접 조작 금지 |
| G-09 | **감사로그 필수** | 중요 관리자/업무 액션은 admin_actions 테이블 기록 필수 |
| G-10 | **Idempotency 필수** | 중복 생성 가능 API(계약/발주/배송 등)는 Idempotency-Key 헤더 필수 |

---

## 기술 스택 고정

```
Frontend:  Next.js (apps/ops-web, apps/arki-web)
Backend:   FastAPI (apps/api)
Database:  PostgreSQL
Cache:     Redis (선택적, Phase 2 이후)
File:      Google Drive or S3-compatible storage
Issue:     GitHub Issues
Sheets:    Google Sheets (보조 레이어)
```

---

## 절대 금지 행위

```
❌ Arkistore 업무 로직과 JH Ops 로직 합치기
❌ Google Sheets를 원본 DB처럼 사용
❌ GitHub을 운영 원본 저장소처럼 사용
❌ 검증 안 된 외부 API 임의 구현
❌ 중요 액션의 감사로그 누락
❌ 중복 생성 가능 API에서 Idempotency 생략
❌ 여러 도메인을 하나의 generic 파일로 뭉개기
❌ 모든 로직을 하나의 거대한 service 파일에 집어넣기
❌ 승인 없이 구현 순서 변경
❌ 불필요한 프레임워크 추가
❌ as any, @ts-ignore, @ts-expect-error 사용
❌ 빈 catch 블록 catch(e) {}
❌ 실패하는 테스트 삭제로 통과 처리
```

---

## 구현 단계 순서 (변경 금지)

```
Phase 1: repo bootstrap, docs, FastAPI skeleton, Next.js skeleton, auth/core/db
Phase 2: projects/project_sites, dashboard summary, customers/consultations/contracts
Phase 3: products/inventory/purchase_requests/purchase_orders/invoices/shipments
Phase 4: deliveries/capacity_slots/happy_calls
Phase 5: error_reports/issue_groups/github_issues/event_logs/admin_actions
Phase 6: files presign, sheet sync jobs, external integration adapters
Phase 7: ops-web frontend
Phase 8: arki-web frontend
Phase 9: 시트 동기화 현실화, 외부 연동 현실화
```

---

*최종 업데이트: 2026-03-11*
*이 문서 변경 시 팀 전체 승인 필요*
