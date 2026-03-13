"""
FastAPI 미들웨어: request_id, trace_id, 에러 캡처, 로깅
"""
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.responses import error_response


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    모든 요청에 request_id와 trace_id 주입
    처리 시간 로깅
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        trace_id = request.headers.get("X-Trace-ID", request_id)

        # request state에 주입
        request.state.request_id = request_id
        request.state.trace_id = trace_id

        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time

        # 응답 헤더에 추가
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        return response


class CatchAllExceptionMiddleware(BaseHTTPMiddleware):
    """
    처리되지 않은 예외를 JSON 응답으로 변환
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            import json

            request_id = getattr(request.state, "request_id", None)
            trace_id = getattr(request.state, "trace_id", None)

            body = error_response(
                code="INTERNAL_SERVER_ERROR",
                message="Internal server error",
                trace_id=trace_id,
                request_id=request_id,
            )

            return Response(
                content=json.dumps(body),
                status_code=500,
                media_type="application/json",
            )
