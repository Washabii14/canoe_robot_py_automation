"""Shared flashing state machine primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class FlashResult:
    success: bool
    step: str
    reason: str = ""
    history: List[str] | None = None
    aborted: bool = False


class FlashStateMachine:
    """Flashing coordinator with explicit transition guards."""

    TRANSITIONS: Dict[str, set[str]] = {
        "idle": {"session"},
        "session": {"security_seed"},
        "security_seed": {"security_key"},
        "security_key": {"download"},
        "download": {"transfer"},
        "transfer": {"transfer", "transfer_exit"},
        "transfer_exit": {"complete"},
    }

    def __init__(self) -> None:
        self.current_step = "idle"
        self.history: List[str] = ["idle"]

    def can_advance(self, next_step: str) -> bool:
        return next_step in self.TRANSITIONS.get(self.current_step, set())

    def advance(self, next_step: str) -> None:
        if not self.can_advance(next_step):
            raise ValueError(
                f"Invalid flashing transition: {self.current_step} -> {next_step}"
            )
        self.current_step = next_step
        self.history.append(next_step)

    def success(self) -> FlashResult:
        return FlashResult(
            success=True, step=self.current_step, reason="", history=list(self.history), aborted=False
        )

    def fail(self, reason: str, aborted: bool = False) -> FlashResult:
        return FlashResult(
            success=False,
            step=self.current_step,
            reason=reason,
            history=list(self.history),
            aborted=aborted,
        )
