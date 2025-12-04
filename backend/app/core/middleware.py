"""
커스텀 미들웨어 (요청/응답 로깅 등)
"""
from __future__ import annotations

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

access_logger = logging.getLogger("app.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    요청/응답 로깅 미들웨어

    - 메서드, 경로, 상태코드, 처리시간(ms), X-Request-ID를 로그로 남김
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # 요청 ID를 상태에 저장해 downstream에서 활용 가능
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        except Exception as exc:  # pragma: no cover - 로깅 용도
            process_time = (time.time() - start_time) * 1000
            access_logger.exception(
                "REQUEST FAILED method=%s path=%s status=%s duration_ms=%.2f request_id=%s",
                request.method,
                request.url.path,
                500,
                process_time,
                request_id,
            )
            raise exc

        process_time = (time.time() - start_time) * 1000

        access_logger.info(
            "REQUEST method=%s path=%s status=%s duration_ms=%.2f request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
            request_id,
        )

        # 응답 헤더에 Request ID 추가
        response.headers["X-Request-ID"] = request_id
        return response


