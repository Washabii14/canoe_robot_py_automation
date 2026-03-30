"""Robot-facing keyword library for CAN flashing."""

from __future__ import annotations

import json
from typing import Any, Dict

from libraries.diagnostics.uds_core import UdsRuntimeConfig, build_client
from libraries.software_update.flash_can import CanFlasher


class FlashKeywordLibrary:
    """Expose flashing operations to Robot with backend-independent setup."""

    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(
        self,
        backend: str = "mock",
        transport: str = "can",
        fixture_path: str = "config/fixtures/uds_mock_responses.json",
        canoe_config_path: str = "",
        auto_measurement: bool | str = True,
        diagnostic_method: str = "",
        request_timeout_s: float | str = 2.0,
        retry_count: int | str = 1,
        retry_delay_s: float | str = 0.2,
    ) -> None:
        self._uds_client = build_client(
            UdsRuntimeConfig(
                backend=backend,
                transport=transport,
                fixture_path=fixture_path,
                canoe_config_path=canoe_config_path or None,
                auto_measurement=_to_bool(auto_measurement),
                diagnostic_method=diagnostic_method or None,
                request_timeout_s=_to_float(request_timeout_s, default=2.0),
                retry_count=_to_int(retry_count, default=1),
                retry_delay_s=_to_float(retry_delay_s, default=0.2),
            )
        )
        self._flasher = CanFlasher(self._uds_client)
        self._last_result: Dict[str, Any] | None = None

    def connect_flashing(self) -> None:
        self._uds_client.connect()

    def disconnect_flashing(self) -> None:
        self._uds_client.disconnect()

    def start_can_flashing(self, image_meta: Any = "{}") -> Dict[str, Any]:
        plan = _safe_json_object(image_meta)
        result = self._flasher.start(plan)
        self._last_result = {
            "success": result.success,
            "step": result.step,
            "reason": result.reason,
            "history": result.history or [],
            "aborted": result.aborted,
        }
        return self._last_result

    def verify_flashing_result(self, expected: bool | str = True) -> Dict[str, Any]:
        if self._last_result is None:
            raise AssertionError("No flashing result available. Run Start CAN Flashing first.")

        expected_bool = _to_bool(expected)
        actual = bool(self._last_result.get("success", False))
        if actual != expected_bool:
            raise AssertionError(
                f"Flashing success mismatch: expected={expected_bool}, actual={actual}, "
                f"result={self._last_result}"
            )
        return self._last_result


def _safe_json_object(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _to_bool(value: bool | str) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: int | str, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(parsed, 0)


def _to_float(value: float | str, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(parsed, 0.0)
