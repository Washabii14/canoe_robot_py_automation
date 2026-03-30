"""Transport-agnostic UDS client abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Dict

from libraries.base.canoe_client import CanoeClient
from libraries.base.transport_interface import TransportAdapter, TransportResponse, UdsRequest
from libraries.diagnostics.uds_can import AdapterPolicy as CanAdapterPolicy
from libraries.diagnostics.uds_can import UdsCanAdapter
from libraries.diagnostics.uds_doip import AdapterPolicy as DoipAdapterPolicy
from libraries.diagnostics.uds_doip import UdsDoipAdapter
from libraries.diagnostics.uds_mock import UdsMockAdapter


@dataclass
class UdsResponse:
    service: str
    payload: str
    positive: bool
    nrc: str | None
    transport: str
    elapsed_ms: float


@dataclass
class UdsRuntimeConfig:
    backend: str
    transport: str
    fixture_path: str = "config/fixtures/uds_mock_responses.json"
    canoe_config_path: str | None = None
    auto_measurement: bool = True
    diagnostic_method: str | None = None
    request_timeout_s: float = 2.0
    retry_count: int = 1
    retry_delay_s: float = 0.2


class UdsClient:
    """Common UDS entrypoint used by Robot keywords."""

    def __init__(self, adapter: TransportAdapter, transport_name: str) -> None:
        self.adapter = adapter
        self.transport_name = transport_name
        self._connected = False

    def connect(self) -> None:
        if not self._connected:
            self.adapter.connect()
            self._connected = True

    def disconnect(self) -> None:
        if self._connected:
            self.adapter.disconnect()
            self._connected = False

    def send_raw(self, bytes_req: str) -> UdsResponse:
        """Send a raw UDS payload represented as hex string."""
        self.connect()
        start = perf_counter()
        raw_resp = self.adapter.send(UdsRequest(mode="raw", request=bytes_req))
        return self.normalize_response(raw_resp, elapsed_ms=(perf_counter() - start) * 1000.0)

    def send_symbolic(self, name: str, params: Dict[str, Any] | None = None) -> UdsResponse:
        """Send a symbolic diagnostic request."""
        self.connect()
        start = perf_counter()
        raw_resp = self.adapter.send(
            UdsRequest(mode="symbolic", name=name, params=params or {})
        )
        return self.normalize_response(raw_resp, elapsed_ms=(perf_counter() - start) * 1000.0)

    def normalize_response(self, raw_resp: TransportResponse, elapsed_ms: float) -> UdsResponse:
        """Map transport-specific payloads into a common response model."""
        return UdsResponse(
            service=raw_resp.service,
            payload=raw_resp.payload,
            positive=raw_resp.positive,
            nrc=raw_resp.nrc,
            transport=self.transport_name,
            elapsed_ms=elapsed_ms,
        )


def build_client(config: UdsRuntimeConfig) -> UdsClient:
    """Factory for mock and live UDS clients with validation."""
    backend = config.backend.strip().lower()
    transport = config.transport.strip().lower()

    if backend not in {"mock", "live"}:
        raise ValueError("backend must be one of: mock, live")
    if transport not in {"can", "doip"}:
        raise ValueError("transport must be one of: can, doip")

    if backend == "mock":
        fixture = Path(config.fixture_path)
        adapter: TransportAdapter = UdsMockAdapter(fixture_path=str(fixture))
        return UdsClient(adapter=adapter, transport_name=transport)

    canoe_client = CanoeClient(
        config_path=config.canoe_config_path,
        auto_measurement=config.auto_measurement,
        diagnostic_method=config.diagnostic_method,
    )
    if transport == "can":
        adapter = UdsCanAdapter(
            canoe_client=canoe_client,
            policy=CanAdapterPolicy(
                timeout_s=config.request_timeout_s,
                retry_count=config.retry_count,
                retry_delay_s=config.retry_delay_s,
            ),
        )
    else:
        adapter = UdsDoipAdapter(
            canoe_client=canoe_client,
            policy=DoipAdapterPolicy(
                timeout_s=max(config.request_timeout_s, 3.0),
                retry_count=config.retry_count,
                retry_delay_s=config.retry_delay_s,
            ),
        )
    return UdsClient(adapter=adapter, transport_name=transport)
