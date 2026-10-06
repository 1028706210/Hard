from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network
import socket
from typing import Protocol


_RFC1918 = (
    IPv4Network("10.0.0.0/8"),
    IPv4Network("172.16.0.0/12"),
    IPv4Network("192.168.0.0/16"),
)
_WARNING = "同一网络设备可访问数据并运行代码。"


class NetworkConfigurationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class LanLauncher(Protocol):
    def start(self, host: str, port: int) -> None: ...
    def stop(self) -> None: ...


class DisabledLauncher:
    def start(self, host: str, port: int) -> None:
        """Test-only inert launcher; production injects the managed Uvicorn launcher."""
    def stop(self) -> None: pass


def is_rfc1918_ipv4(value: str) -> bool:
    try:
        address = IPv4Address(value)
    except ValueError:
        return False
    return any(address in network for network in _RFC1918)


def private_ipv4_interfaces() -> tuple[str, ...]:
    addresses: set[str] = set()
    try:
        records = socket.getaddrinfo(socket.gethostname(), None, family=socket.AF_INET)
    except OSError:
        records = []
    for _family, _kind, _protocol, _canonical_name, socket_address in records:
        candidate = socket_address[0]
        if is_rfc1918_ipv4(candidate):
            addresses.add(candidate)
    return tuple(sorted(addresses))


@dataclass(frozen=True, slots=True)
class LanStatus:
    enabled: bool
    bind_host: str
    port: int
    url: str | None
    interfaces: tuple[str, ...]
    warning: str
    firewall_preview: str
    firewall_revoke_preview: str

    def as_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "bind_host": self.bind_host,
            "port": self.port,
            "url": self.url,
            "interfaces": list(self.interfaces),
            "warning": self.warning,
            "firewall_preview": self.firewall_preview,
            "firewall_revoke_preview": self.firewall_revoke_preview,
        }


class LanAccessController:
    """Starts only a validated private listener; it never changes Windows Firewall."""

    def __init__(self, *, interfaces: Callable[[], tuple[str, ...]] = private_ipv4_interfaces, port: int = 8000, launcher: LanLauncher | None = None) -> None:
        self._interfaces = interfaces
        self._port = port
        self._enabled_host: str | None = None
        self._last_key: str | None = None
        self._last_requested_port: int | None = None
        self._launcher = launcher or DisabledLauncher()
        self.firewall_execution_count = 0

    def status(self) -> dict[str, object]:
        interfaces = tuple(host for host in self._interfaces() if is_rfc1918_ipv4(host))
        host = self._enabled_host or "127.0.0.1"
        return LanStatus(
            enabled=self._enabled_host is not None,
            bind_host=host,
            port=self._port,
            url=f"http://{host}:{self._port}" if self._enabled_host is not None else None,
            interfaces=interfaces,
            warning=_WARNING,
            firewall_preview=(
                "New-NetFirewallRule -DisplayName 'Hard Private LAN' -Direction Inbound "
                f"-Action Allow -Protocol TCP -LocalPort {self._port} -Profile Private"
            ),
            firewall_revoke_preview="Remove-NetFirewallRule -DisplayName 'Hard Private LAN'",
        ).as_dict()

    def enable(
        self,
        host: str,
        *,
        confirmed: bool,
        idempotency_key: str,
        requested_port: int | None = None,
    ) -> dict[str, object]:
        port = self._port if requested_port is None else requested_port
        if not confirmed:
            raise NetworkConfigurationError("lan_confirmation_required", "必须确认局域网访问风险。")
        if self._last_key == idempotency_key:
            if host != self._enabled_host or port != self._last_requested_port:
                raise NetworkConfigurationError("idempotency_conflict", "幂等键不能用于不同的局域网配置。")
            return self.status()
        if port != self._port or not is_rfc1918_ipv4(host) or host not in self._interfaces():
            raise NetworkConfigurationError("invalid_lan_host", "只能选择已验证的 RFC1918 私有 IPv4 接口。")
        self._launcher.start(host, port)
        self._enabled_host = host
        self._last_key = idempotency_key
        self._last_requested_port = port
        return self.status()

    def disable(self) -> dict[str, object]:
        self._launcher.stop()
        self._enabled_host = None
        self._last_key = None
        self._last_requested_port = None
        return self.status()
