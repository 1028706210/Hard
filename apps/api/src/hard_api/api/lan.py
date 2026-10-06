from __future__ import annotations

from fastapi import APIRouter, Header, Request
from pydantic import BaseModel

from hard_api.core.errors import ApiError
from hard_api.core.network import NetworkConfigurationError


router = APIRouter(prefix="/api/lan", tags=["lan"])


def _response(title: str) -> dict[int, dict[str, object]]:
    return {200: {"content": {"application/json": {"schema": {"type": "object", "title": title, "additionalProperties": True}}}}}


class LanEnableRequest(BaseModel):
    host: str
    confirmed: bool


class LanStatusResponse(BaseModel):
    enabled: bool
    bind_host: str
    port: int
    url: str | None
    interfaces: list[str]
    warning: str
    firewall_preview: str
    firewall_revoke_preview: str


def _key(value: str | None) -> str:
    if value is None or not 1 <= len(value) <= 128:
        raise ApiError("invalid_idempotency_key", "幂等键不合法。")
    return value


@router.get("/status", response_model=LanStatusResponse, responses=_response("LanStatusResponse"))
def status(request: Request) -> dict[str, object]:
    return request.app.state.lan_controller.status()


@router.post("/enable", response_model=LanStatusResponse, responses=_response("LanEnableResponse"))
def enable(
    payload: LanEnableRequest,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, object]:
    try:
        return request.app.state.lan_controller.enable(
            payload.host,
            confirmed=payload.confirmed,
            idempotency_key=_key(idempotency_key),
        )
    except NetworkConfigurationError as error:
        raise ApiError(error.code, str(error)) from error


@router.delete("/enable", response_model=LanStatusResponse, responses=_response("LanDisableResponse"))
def disable(request: Request) -> dict[str, object]:
    return request.app.state.lan_controller.disable()
