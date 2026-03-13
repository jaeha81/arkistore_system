# ============================================================
# Arkistore Operations API — Dockerfile
# Multi-stage build (builder → runtime)
# ============================================================

# ── Stage 1: builder ────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# 시스템 의존성 (C 확장 빌드용)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드 + wheel 설치
RUN pip install --upgrade pip wheel

# 패키지 먼저 복사 (레이어 캐시 활용)
COPY pyproject.toml ./
RUN pip install --no-cache-dir --prefix=/install ".[dev]" || \
    pip install --no-cache-dir --prefix=/install .

# ── Stage 2: runtime ────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# 런타임 시스템 의존성만
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# builder 에서 설치된 패키지 복사
COPY --from=builder /install /usr/local

# 소스 코드 복사
COPY . .

# 비루트 사용자
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app
USER appuser

# 포트
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 실행 (프로덕션: gunicorn + uvicorn workers)
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--keepalive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
