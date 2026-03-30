"""Deterministic fixture-backed transport adapter for offline tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from libraries.base.transport_interface import TransportAdapter, TransportResponse, UdsRequest


class UdsMockAdapter(TransportAdapter):
    """Fixture-backed adapter keyed by request identifier."""

    def __init__(self, fixture_path: str) -> None:
        self.fixture_path = Path(fixture_path)
        self._connected = False
        self._fixtures: Dict[str, Dict[str, Any]] = {}

    def connect(self) -> None:
        if not self.fixture_path.exists():
            raise FileNotFoundError(f"Fixture not found: {self.fixture_path}")
        self._fixtures = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def send(self, request: UdsRequest) -> TransportResponse:
        if not self._connected:
            raise RuntimeError("Mock adapter is not connected.")

        if request.mode == "raw":
            key = str(request.request or "").strip().upper()
        else:
            key = f"symbolic:{request.name or ''}"

        raw = self._fixtures.get(
            key,
            {
                "service": "unknown",
                "payload": "",
                "positive": False,
                "nrc": "0x31",
            },
        )
        return TransportResponse(
            service=str(raw.get("service", "unknown")),
            payload=str(raw.get("payload", "")),
            positive=bool(raw.get("positive", False)),
            nrc=raw.get("nrc"),
            metadata={"adapter": "mock", "fixture_key": key},
        )
