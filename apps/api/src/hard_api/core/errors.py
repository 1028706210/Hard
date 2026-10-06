from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApiError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = dict(details or {})


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: Mapping[str, Any] | None = None,
) -> JSONResponse:
    request_id = _request_id(request)
    response = JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": dict(details or {}),
                "request_id": request_id,
            }
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


async def api_error_handler(request: Request, error: ApiError) -> JSONResponse:
    return error_response(
        request,
        status_code=error.status_code,
        code=error.code,
        message=error.message,
        details=error.details,
    )


async def http_error_handler(
    request: Request, error: StarletteHTTPException
) -> JSONResponse:
    if error.status_code == 404:
        return error_response(
            request,
            status_code=404,
            code="not_found",
            message="未找到请求的资源。",
        )
    return error_response(
        request,
        status_code=error.status_code,
        code="http_error",
        message="请求无法完成。",
    )


async def unhandled_error_handler(request: Request, error: Exception) -> JSONResponse:
    logging.getLogger("hard_api").exception("Unhandled API error", exc_info=error)
    return error_response(
        request,
        status_code=500,
        code="internal_error",
        message="服务器内部错误。",
    )
