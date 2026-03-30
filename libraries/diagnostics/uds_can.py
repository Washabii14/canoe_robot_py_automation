"""UDS over CAN/CAN-FD adapter with retry and timeout policy."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass

from libraries.base.canoe_client import CanoeClient
from libraries.base.transport_interface import TransportAdapter, TransportResponse, UdsRequest


@dataclass
class AdapterPolicy:
    """Runtime policy for live diagnostic transport calls."""

    timeout_s: float = 2.0
    retry_count: int = 1
    retry_delay_s: float = 0.2


class UdsCanAdapter(TransportAdapter):
    """CAN transport adapter for live CANoe integration."""

    def __init__(self, canoe_client: CanoeClient, policy: AdapterPolicy | None = None) -> None:
        self.canoe_client = canoe_client
        self.policy = policy or AdapterPolicy()
        self._connected = False

    def connect(self) -> None:
        if self._connected:
            return
        self.canoe_client.open()
        self._connected = True

    def disconnect(self) -> None:
        if not self._connected:
            return
        self.canoe_client.close()
        self._connected = False

    def send(self, request: UdsRequest) -> TransportResponse:
        attempt = 0
        last_error: Exception | None = None
        while attempt <= self.policy.retry_count:
            start = time.perf_counter()
            try:
                raw = self.canoe_client.send_diagnostic_request(
                    transport="can",
                    mode=request.mode,
                    request=request.request,
                    name=request.name,
                    params=request.params,
                )
                elapsed_s = time.perf_counter() - start
                if elapsed_s > self.policy.timeout_s:
                    raise TimeoutError(
                        f"CAN request exceeded timeout ({elapsed_s:.3f}s > {self.policy.timeout_s:.3f}s)"
                    )
                return _to_transport_response(raw=raw, adapter="can", attempt=attempt + 1)
            except Exception as exc:
                last_error = exc
                if attempt >= self.policy.retry_count:
                    break
                time.sleep(self.policy.retry_delay_s)
                attempt += 1

        assert last_error is not None
        raise RuntimeError(f"CAN diagnostic request failed after {attempt + 1} attempts") from last_error


def _to_transport_response(raw: dict, adapter: str, attempt: int) -> TransportResponse:
    payload = str(raw.get("payload", ""))
    nrc = raw.get("nrc") or _extract_nrc(payload)
    positive = bool(raw.get("positive", nrc is None))
    if nrc is not None:
        positive = False
    metadata = {"adapter": adapter, "attempt": attempt, **raw.get("metadata", {})}
    return TransportResponse(
        service=str(raw.get("service", "unknown")),
        payload=payload,
        positive=positive,
        nrc=nrc,
        metadata=metadata,
    )


def _extract_nrc(payload: str) -> str | None:
    compact = "".join(re.findall(r"[0-9A-Fa-f]{2}", payload)).upper()
    if compact.startswith("7F") and len(compact) >= 6:
        return f"0x{compact[4:6]}"
    return None
