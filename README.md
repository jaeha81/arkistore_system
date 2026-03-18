# Arkistore Operations Automation System

> Arkistore 가구/인테리어 업체의 물류·영업·판매 실무를 디지털화하고,  
> JH 운영팀이 개발·배포·이슈를 통합 관제하는 이중 구조 풀스택 플랫폼.

---

## 시스템 구성

```
┌─────────────────────────────────────────────────────────────┐
│                Arkistore Operations Platform                 │
├───────────────────┬──────────────────┬──────────────────────┤
│   arki-web        │   ops-web        │   api (FastAPI)      │
│   포트 3001        │   포트 3000       │   포트 8000           │
│                   │                  │                      │
│ Arkistore 업무     │ JH 운영관리       │ PostgreSQL 15        │
│ 시스템             │ 대시보드          │ Redis                │
│ · 물류             │ · 프로젝트 관리   │ JWT Auth             │
│ · 영업             │ · 이슈/GitHub     │ S3 스토리지           │
│ · 판매매니저       │ · 배포 기록       │                      │
│ · 대시보드         │ · 이벤트 로그     │                      │
└───────────────────┴──────────────────┴──────────────────────┘
```

---

## 주요 기능

### arki-web — Arkistore 업무 시스템

| 카테고리 | 기능 |
|---------|------|
| **물류** | 상품 마스터, 재고 현황, 발주 요청, 발주서 관리, 인보이스, BL/선적 관리 |
| **영업** | 고객 관리 (VIP/등급), 문의/리드, 배송 관리, 배송 CAPA 슬롯 |
| **판매매니저** | 상담 관리, 계약 관리 (첨부파일 포함), 해피콜 |
| **대시보드** | 실시간 KPI 5종, recharts 차트 3종 (배송추이·계약상태·발주상태), 60초 자동 새로고침 |
| **생산성** | CSV 내보내기 (6개 메뉴), 알림 벨 (재고부족·신규문의·CAPA 경고) |
| **UX** | 모바일 반응형 레이아웃, 사이드바 오버레이 |

### ops-web — JH 운영관리 대시보드

| 카테고리 | 기능 |
|---------|------|
| **이슈 관리** | 오류 그룹화, 개별 이슈 추적, GitHub 이슈 자동 생성 |
| **배포 기록** | 배포 이벤트 이력, 메타데이터 조회 |
| **로그** | 이벤트 로그, 오류 로그 상세 조회 |
| **프로젝트** | 운영 프로젝트 등록 및 상태 관리 |

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| **Frontend** | Next.js 14 (App Router), TypeScript, TailwindCSS, Recharts |
| **Backend** | FastAPI 0.110+, Python 3.11+, Pydantic v2 |
| **Database** | PostgreSQL 15+, SQLAlchemy 2.x (Mapped[] 타입), Alembic |
| **인증** | JWT (httpOnly cookie), bcrypt |
| **외부 연동** | GitHub API, Google Sheets API, S3-compatible Storage |
| **연동 Mock** | Ecount ERP, 나인유나이티드 배송, UNI-PASS 관세청 |
| **인프라** | Docker, docker-compose, Nginx (TLS 1.2/1.3, HSTS) |
| **CI/CD** | GitHub Actions (pytest → Docker 빌드 → SSH 배포, Vercel 자동 배포) |
| **테스트** | pytest-asyncio, httpx, SQLite in-memory |

---

## 빠른 시작 — Docker Compose (권장)

```bash
git clone https://github.com/jaeha81/arkistore_system.git
cd arkistore_system

# 1. 환경변수 설정
cp apps/api/.env.example apps/api/.env
# apps/api/.env 편집: JWT_SECRET_KEY 변경 권장 (나머지 기본값으로 동작)

# 2. 전체 스택 실행 (DB → Redis → 마이그레이션 → API 순서 자동)
docker compose up -d

# 3. 초기 데이터 시드 (계정 5개 + 샘플 제품 + CAPA 슬롯 30일치)
cd apps/api
python -m pip install -e ".[dev]"
python scripts/seed.py

# 4. 프론트엔드 실행 (별도 터미널)
cd apps/arki-web && npm install && npm run dev   # → http://localhost:3001
cd apps/ops-web  && npm install && npm run dev   # → http://localhost:3000
```

| 접속 URL | 설명 |
|---------|------|
| http://localhost:3001 | Arkistore 업무 시스템 |
| http://localhost:3000 | JH 운영관리 대시보드 |
| http://localhost:8000/docs | FastAPI Swagger 문서 |
| http://localhost:8000/health | 헬스체크 |

---

## 초기 로그인 계정

| 역할 | 이메일 | 비밀번호 |
|------|--------|---------|
| super_admin | admin@arkistore.com | Admin1234! |
| ops_admin | ops@arkistore.com | Ops12345! |
| arki_logistics | logistics@arkistore.com | Arki1234! |
| arki_sales | sales@arkistore.com | Arki1234! |
| arki_store_manager | manager@arkistore.com | Arki1234! |

> **운영 배포 전 반드시 비밀번호를 변경하세요.**

---

## 수동 실행 (Docker 없이)

```bash
# 1. PostgreSQL
docker run -d --name arkistore-db \
  -e POSTGRES_USER=arkistore \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=arkistore_db \
  -p 5432:5432 \
  postgres:15-alpine

# 2. 백엔드
cd apps/api
cp .env.example .env
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3. 시드 데이터
python scripts/seed.py

# 4. 프론트엔드 (별도 터미널 x2)
cd apps/arki-web && npm install && npm run dev   # 포트 3001
cd apps/ops-web  && npm install && npm run dev   # 포트 3000
```

---

## 외부 연동 Mock 전환

개발/스테이징 환경에서는 Mock 모드로 동작합니다. `apps/api/.env`에서 전환:

```env
USE_MOCK_ECOUNT=true        # false → 실제 Ecount ERP API
USE_MOCK_NINE_UNITED=true   # false → 실제 나인유나이티드 배송 포털
USE_MOCK_CUSTOMS=true       # false → 실제 UNI-PASS 관세청 통관조회
```

실제 연동 시 필요한 키:

```env
GITHUB_TOKEN=<GitHub Personal Access Token>
GOOGLE_SERVICE_ACCOUNT_JSON=<GCP 서비스계정 JSON 경로>
ECOUNT_COM_CODE=<Ecount 회사코드>
ECOUNT_API_KEY=<Ecount API 키>
NINE_UNITED_API_KEY=<나인유나이티드 API 키>
UNIPASS_API_KEY=<관세청 UNI-PASS API 키>
```

---

## 프로덕션 배포

### 가장 빠른 배포 (30분 목표)

1. **Supabase** — PostgreSQL 무료 인스턴스 생성 → `DATABASE_URL` 설정
2. **Upstash** — Redis 무료 인스턴스 생성 → `REDIS_URL` 설정
3. **Railway** — GitHub 레포 연결 → 환경변수 입력 → 자동 Docker 배포
4. **Vercel** — arki-web / ops-web 각각 프로젝트 생성 → `NEXT_PUBLIC_API_URL` 설정
5. Railway 콘솔: `alembic upgrade head` 실행
6. Railway 콘솔: `python scripts/seed.py` 실행

### 환경변수 (프로덕션 필수)

```env
DATABASE_URL=postgresql+asyncpg://[운영DB주소]
REDIS_URL=redis://[운영Redis주소]
JWT_SECRET_KEY=[64자 이상 랜덤 문자열]
APP_ENV=production
CORS_ORIGINS=["https://ops.arkistore.com","https://app.arkistore.com"]
COOKIE_DOMAIN=.arkistore.com
COOKIE_SECURE=true
ENCRYPTION_KEY=[Fernet 키 — 고객 개인정보 마스킹용]
```

Fernet 키 생성:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### GitHub Actions 자동 배포

`.github/workflows/`에 이미 포함:

| 워크플로 | 트리거 | 동작 |
|---------|--------|------|
| `deploy.yml` | main 브랜치 push | pytest → Docker 빌드 → GHCR 푸시 → SSH 배포 |
| `frontend.yml` | ops-web/arki-web 파일 변경 | Vercel 프로덕션 자동 배포 |

GitHub Secrets 등록 필요:
```
DEPLOY_HOST, DEPLOY_USER, DEPLOY_SSH_KEY
VERCEL_TOKEN, VERCEL_ORG_ID
VERCEL_PROJECT_ID_OPS, VERCEL_PROJECT_ID_ARKI
```

---

## 프로젝트 구조

```
arkistore_system/
├── .github/workflows/
│   ├── deploy.yml          # 백엔드 CI/CD
│   └── frontend.yml        # 프론트 Vercel 배포
├── nginx/
│   ├── nginx.conf
│   └── conf.d/arkistore.conf  # SSL + 리버스 프록시
├── apps/
│   ├── api/                # FastAPI 백엔드
│   │   ├── app/
│   │   │   ├── models/     # 26개 SQLAlchemy 모델
│   │   │   ├── schemas/    # 22개 Pydantic 스키마
│   │   │   ├── repositories/   # 21개
│   │   │   ├── services/   # 25개 (arki 14 + ops 5 + 공통 6)
│   │   │   ├── api/v1/     # 23개 라우터
│   │   │   ├── core/       # config, security, permissions, enums
│   │   │   ├── integrations/   # 15개 (Ecount, NineUnited, UNI-PASS, GitHub, GSheets, S3)
│   │   │   └── db/migrations/  # Alembic 마이그레이션
│   │   ├── scripts/seed.py
│   │   ├── tests/          # 9개 pytest 파일
│   │   ├── .env.example
│   │   └── Dockerfile
│   ├── arki-web/           # Next.js 14 (포트 3001)
│   │   ├── app/arki/       # 37개 페이지
│   │   ├── components/     # UI + layout
│   │   └── lib/            # api.ts, exportCsv.ts, cn.ts
│   └── ops-web/            # Next.js 14 (포트 3000)
│       ├── app/ops/        # 14개 페이지
│       ├── components/     # UI + layout
│       └── lib/            # api.ts, utils.ts
├── docs/                   # 설계 문서 14개
├── packages/               # 공유 타입/Tailwind 설정
├── docker-compose.yml
└── Makefile
```

---

## 설계 원칙

`docs/00_GUARDRAILS.md` 참조. 핵심 원칙:

- **도메인 분리**: Arkistore 업무(arki-web) ↔ JH 운영(ops-web) 코드 절대 혼합 금지
- **Mock-First**: 외부 연동은 Adapter 패턴 + Mock 기본값 (운영 전환은 `.env`로 제어)
- **Idempotency-Key 필수** API: contracts, purchase_requests, purchase_orders, deliveries, error_reports
- **Google Sheets는 보조**: 원본 데이터는 항상 PostgreSQL

---

## 테스트

```bash
cd apps/api
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## 라이선스

Private — Arkistore / JH 내부 사용 전용

---

## 📊 개발 현황 <!-- jh-progress -->

| 항목 | 내용 |
|------|------|
| **진행률** | `████████████████████` **100%** |
| **레포** | [arkistore_system](https://github.com/jaeha81/arkistore_system) |

> 진행률: 100%
