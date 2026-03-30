"""Common transport contracts for CAN, DoIP, and mock adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any, Dict


@dataclass
class UdsRequest:
    """Normalized request payload independent of transport."""

    mode: str
    request: str | None = None
    name: str | None = None
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransportResponse:
    """Normalized transport response payload."""

    service: str
    payload: str
    positive: bool
    nrc: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TransportAdapter(ABC):
    """Adapter boundary used by UDS client implementations."""

    @abstractmethod
    def connect(self) -> None:
        """Open transport resources."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Close transport resources."""
        raise NotImplementedError

    @abstractmethod
    def send(self, request: UdsRequest) -> TransportResponse:
        """Send a normalized request and return a normalized response."""
        raise NotImplementedError
