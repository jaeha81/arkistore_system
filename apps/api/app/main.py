"""
Arkistore Operations API - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.idempotency import IdempotencyReplayException
from app.core.middleware import RequestContextMiddleware
from app.core.responses import error_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 이벤트"""
    # Startup
    print(f"Starting Arkistore API [{settings.APP_ENV}]")
    yield
    # Shutdown
    print("Shutting down Arkistore API")


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="""
Arkistore Operations API

두 계층으로 구성됩니다:
- `/api/v1/ops/*`: JH 운영관리 도메인
- `/api/v1/arki/*`: Arkistore 업무 도메인
    """,
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ==================== Middleware ====================

app.add_middleware(RequestContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Trace-ID", "X-Process-Time"],
)

# ==================== Exception Handlers ====================


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    trace_id = getattr(request.state, "trace_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            trace_id=trace_id,
            request_id=request_id,
        ),
    )


@app.exception_handler(IdempotencyReplayException)
async def idempotency_replay_handler(
    request: Request, exc: IdempotencyReplayException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.cached_response,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    trace_id = getattr(request.state, "trace_id", None)
    return JSONResponse(
        status_code=500,
        content=error_response(
            code="INTERNAL_SERVER_ERROR",
            message="Internal server error",
            trace_id=trace_id,
            request_id=request_id,
        ),
    )


# ==================== Routers ====================

from app.api.v1.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api/v1")


# ==================== Health Check ====================


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "env": settings.APP_ENV, "version": settings.APP_VERSION}
