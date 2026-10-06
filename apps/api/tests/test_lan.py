from __future__ import annotations

import sys
from pathlib import Path
from urllib.request import urlopen

from fastapi.testclient import TestClient
import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hard_api.core.network import LanAccessController, NetworkConfigurationError, is_rfc1918_ipv4
from hard_api.main import _UvicornLanLauncher, create_app


def test_lan_defaults_to_loopback_and_accepts_only_verified_rfc1918_interfaces() -> None:
    controller = LanAccessController(interfaces=lambda: ("192.168.10.8", "10.2.3.4"), port=8000)

    assert controller.status()["enabled"] is False
    assert controller.status()["bind_host"] == "127.0.0.1"
    assert is_rfc1918_ipv4("10.2.3.4") is True
    assert is_rfc1918_ipv4("172.16.0.1") is True
    assert is_rfc1918_ipv4("192.168.1.1") is True
    for value in ("0.0.0.0", "127.0.0.1", "169.254.1.2", "8.8.8.8", "::1"):
        assert is_rfc1918_ipv4(value) is False
        with pytest.raises(NetworkConfigurationError):
            controller.enable(value, confirmed=True, idempotency_key=f"key-{value}")


def test_lan_requires_explicit_confirmation_and_never_executes_firewall_commands() -> None:
    controller = LanAccessController(interfaces=lambda: ("192.168.10.8",), port=8000)
    with pytest.raises(NetworkConfigurationError, match="确认"):
        controller.enable("192.168.10.8", confirmed=False, idempotency_key="lan-1")

    status = controller.enable("192.168.10.8", confirmed=True, idempotency_key="lan-1")
    replay = controller.enable("192.168.10.8", confirmed=True, idempotency_key="lan-1")

    assert status == replay
    assert status["url"] == "http://192.168.10.8:8000"
    assert "-Profile Private" in status["firewall_preview"]
    assert "Remove-NetFirewallRule" in status["firewall_revoke_preview"]
    assert controller.firewall_execution_count == 0
    with pytest.raises(NetworkConfigurationError, match="幂等"):
        controller.enable("192.168.10.8", confirmed=True, idempotency_key="lan-1", requested_port=9000)


def test_lan_api_rejects_unsafe_bindings_and_returns_a_warning_with_a_private_url() -> None:
    app = create_app()
    app.state.lan_controller = LanAccessController(interfaces=lambda: ("192.168.10.8",), port=8000)

    with TestClient(app) as client:
        initial = client.get("/api/lan/status")
        missing_confirmation = client.post(
            "/api/lan/enable",
            json={"host": "192.168.10.8", "confirmed": False},
            headers={"Idempotency-Key": "lan-confirm"},
        )
        public = client.post(
            "/api/lan/enable",
            json={"host": "8.8.8.8", "confirmed": True},
            headers={"Idempotency-Key": "lan-public"},
        )
        enabled = client.post(
            "/api/lan/enable",
            json={"host": "192.168.10.8", "confirmed": True},
            headers={"Idempotency-Key": "lan-private"},
        )

    assert initial.status_code == 200
    assert initial.json()["bind_host"] == "127.0.0.1"
    assert missing_confirmation.status_code == 400
    assert missing_confirmation.json()["error"]["code"] == "lan_confirmation_required"
    assert public.status_code == 400
    assert public.json()["error"]["code"] == "invalid_lan_host"
    assert enabled.status_code == 200
    assert enabled.json()["url"] == "http://192.168.10.8:8000"
    assert "同一网络设备可访问数据并运行代码" in enabled.json()["warning"]


def test_lan_controller_manages_injected_service_lifecycle_without_firewall_execution() -> None:
    events: list[tuple[str, str | None, int | None]] = []
    class Launcher:
        def start(self, host: str, port: int) -> None: events.append(("start", host, port))
        def stop(self) -> None: events.append(("stop", None, None))
    controller = LanAccessController(interfaces=lambda: ("192.168.10.8",), port=8000, launcher=Launcher())
    assert controller.enable("192.168.10.8", confirmed=True, idempotency_key="lifecycle")["enabled"] is True
    assert controller.disable()["enabled"] is False
    assert events == [("start", "192.168.10.8", 8000), ("stop", None, None)]
    assert controller.firewall_execution_count == 0


def test_real_lan_listener_serves_hard_html_and_api_then_releases_loopback_port(tmp_path: Path) -> None:
    app = create_app()
    frontend = tmp_path / "web"
    frontend.mkdir()
    (frontend / "index.html").write_text("<title>Hard</title><script src='/assets/app.js'></script>", encoding="utf-8")
    (frontend / "assets").mkdir()
    (frontend / "assets" / "app.js").write_text("window.hard = true", encoding="utf-8")
    launcher = _UvicornLanLauncher(app, frontend_root=frontend)
    launcher.start("127.0.0.1", 0)
    assert launcher.server is not None
    port = launcher.server.server_address[1]
    with urlopen(f"http://127.0.0.1:{port}/", timeout=3) as response:
        assert b"<title>Hard</title>" in response.read()
    with urlopen(f"http://127.0.0.1:{port}/lesson/python-foundations-hello-world", timeout=3) as response:
        assert b"<title>Hard</title>" in response.read()
    with urlopen(f"http://127.0.0.1:{port}/assets/app.js", timeout=3) as response:
        assert response.headers["content-type"].startswith("text/javascript")
        assert b"window.hard" in response.read()
    with urlopen(f"http://127.0.0.1:{port}/api/v1/health/live", timeout=3) as response:
        assert response.headers["content-type"].startswith("application/json")
    launcher.stop()
    with pytest.raises(OSError):
        urlopen(f"http://127.0.0.1:{port}/", timeout=1)


def test_lan_start_failure_never_reports_enabled() -> None:
    class BrokenLauncher:
        def start(self, host: str, port: int) -> None:
            raise OSError("port unavailable")
        def stop(self) -> None:
            raise AssertionError("a failed start must not need cleanup")

    controller = LanAccessController(
        interfaces=lambda: ("192.168.10.8",), port=8000, launcher=BrokenLauncher()
    )
    with pytest.raises(OSError, match="port unavailable"):
        controller.enable("192.168.10.8", confirmed=True, idempotency_key="broken")
    assert controller.status()["enabled"] is False


def test_lan_missing_frontend_build_returns_an_actionable_stable_error(tmp_path: Path) -> None:
    app = create_app()
    controller = LanAccessController(
        interfaces=lambda: ("192.168.10.8",),
        port=8000,
        launcher=_UvicornLanLauncher(app, frontend_root=tmp_path / "missing-dist"),
    )

    with pytest.raises(NetworkConfigurationError) as raised:
        controller.enable("192.168.10.8", confirmed=True, idempotency_key="missing-build")

    assert raised.value.code == "lan_frontend_build_required"
    assert "pnpm --dir apps/web build" in str(raised.value)
    assert controller.status()["enabled"] is False
