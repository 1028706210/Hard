import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hard_api.main import create_app


def test_unknown_route_uses_stable_error_body_and_request_id() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/does-not-exist", headers={"X-Request-ID": "audit-request"})

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": "未找到请求的资源。",
            "details": {},
            "request_id": "audit-request",
        }
    }
    assert response.headers["X-Request-ID"] == "audit-request"


def test_unhandled_error_hides_stack_trace_in_response() -> None:
    app = create_app()

    @app.get("/raise-for-test")
    def raise_for_test() -> None:
        raise RuntimeError("private traceback detail")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/raise-for-test")

    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_error"
    assert "private traceback detail" not in response.text
    assert "Traceback" not in response.text
    assert body["error"]["request_id"] == response.headers["X-Request-ID"]
