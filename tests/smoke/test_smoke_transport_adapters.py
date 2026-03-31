"""Smoke checks for transport adapter policy behavior."""

from __future__ import annotations

from typing import Any

from libraries.diagnostics.uds_can import AdapterPolicy as CanPolicy
from libraries.diagnostics.uds_can import UdsCanAdapter
from libraries.diagnostics.uds_doip import AdapterPolicy as DoipPolicy
from libraries.diagnostics.uds_doip import UdsDoipAdapter
from libraries.base.transport_interface import UdsRequest


class _FakeCanoeClient:
    def __init__(self, responses: list[Any]) -> None:
        self.responses = responses
        self.calls = 0
        self.opened = False

    def open(self) -> None:
        self.opened = True

    def close(self) -> None:
        self.opened = False

    def send_diagnostic_request(self, **_: Any) -> dict[str, Any]:
        item = self.responses[self.calls]
        self.calls += 1
        if isinstance(item, Exception):
            raise item
        return item


def test_can_adapter_retries_after_transient_error() -> None:
    fake = _FakeCanoeClient(
        [
            RuntimeError("transient"),
            {"service": "0x22", "payload": "62 F1 90", "positive": True, "nrc": None},
        ]
    )
    adapter = UdsCanAdapter(fake, policy=CanPolicy(timeout_s=1.0, retry_count=1, retry_delay_s=0.0))
    adapter.connect()
    resp = adapter.send(UdsRequest(mode="raw", request="22 F1 90"))
    assert resp.positive is True
    assert fake.calls == 2


def test_doip_adapter_extracts_nrc_from_payload() -> None:
    fake = _FakeCanoeClient(
        [
            {"service": "0x22", "payload": "7F 22 31", "positive": True, "nrc": None},
        ]
    )
    adapter = UdsDoipAdapter(
        fake, policy=DoipPolicy(timeout_s=1.0, retry_count=0, retry_delay_s=0.0)
    )
    adapter.connect()
    resp = adapter.send(UdsRequest(mode="raw", request="22 F1 90"))
    assert resp.positive is False
    assert resp.nrc == "0x31"
