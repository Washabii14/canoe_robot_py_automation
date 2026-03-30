"""Robot-facing diagnostic keyword library."""

from __future__ import annotations

import json
import time
from typing import Any, Dict

from libraries.diagnostics.uds_core import UdsClient, UdsRuntimeConfig, build_client


class DiagKeywordLibrary:
    """Robot library that abstracts backend selection and UDS calls."""

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
        wait_poll_interval_s: float | str = 0.2,
    ) -> None:
        timeout = _to_float(request_timeout_s, default=2.0)
        retry_delay = _to_float(retry_delay_s, default=0.2)
        wait_poll = _to_float(wait_poll_interval_s, default=0.2)
        self._client: UdsClient = build_client(
            UdsRuntimeConfig(
                backend=backend,
                transport=transport,
                fixture_path=fixture_path,
                canoe_config_path=canoe_config_path or None,
                auto_measurement=_to_bool(auto_measurement),
                diagnostic_method=diagnostic_method or None,
                request_timeout_s=timeout,
                retry_count=_to_int(retry_count, default=1),
                retry_delay_s=retry_delay,
            )
        )
        self._default_wait_timeout_s = timeout
        self._default_wait_poll_interval_s = wait_poll

    def connect_diagnostics(self) -> None:
        self._client.connect()

    def disconnect_diagnostics(self) -> None:
        self._client.disconnect()

    def send_raw_uds_request(self, bytes_req: str) -> Dict[str, Any]:
        response = self._client.send_raw(bytes_req)
        return {
            "service": response.service,
            "payload": response.payload,
            "positive": response.positive,
            "nrc": response.nrc,
            "transport": response.transport,
            "elapsed_ms": response.elapsed_ms,
        }

    def send_symbolic_uds_request(self, name: str, params: str = "{}") -> Dict[str, Any]:
        parsed_params = _safe_json_object(params)
        response = self._client.send_symbolic(name=name, params=parsed_params)
        return {
            "service": response.service,
            "payload": response.payload,
            "positive": response.positive,
            "nrc": response.nrc,
            "transport": response.transport,
            "elapsed_ms": response.elapsed_ms,
        }

    def wait_for_raw_uds_positive_response(
        self,
        bytes_req: str,
        timeout_s: float | str = "",
        poll_interval_s: float | str = "",
    ) -> Dict[str, Any]:
        resolved_timeout = _resolve_timeout(
            timeout_s, default=self._default_wait_timeout_s
        )
        resolved_poll = _resolve_poll_interval(
            poll_interval_s, default=self._default_wait_poll_interval_s
        )
        return self._wait_until(
            send_fn=lambda: self.send_raw_uds_request(bytes_req),
            condition_fn=lambda resp: bool(resp.get("positive", False)),
            timeout_s=resolved_timeout,
            poll_interval_s=resolved_poll,
            request_label=bytes_req,
            expected_label="positive response",
        )

    def wait_for_raw_uds_nrc_response(
        self,
        bytes_req: str,
        expected_nrc: str,
        timeout_s: float | str = "",
        poll_interval_s: float | str = "",
    ) -> Dict[str, Any]:
        resolved_timeout = _resolve_timeout(
            timeout_s, default=self._default_wait_timeout_s
        )
        resolved_poll = _resolve_poll_interval(
            poll_interval_s, default=self._default_wait_poll_interval_s
        )
        expected = str(expected_nrc).strip()
        return self._wait_until(
            send_fn=lambda: self.send_raw_uds_request(bytes_req),
            condition_fn=lambda resp: (not bool(resp.get("positive", True)))
            and str(resp.get("nrc")) == expected,
            timeout_s=resolved_timeout,
            poll_interval_s=resolved_poll,
            request_label=bytes_req,
            expected_label=f"NRC {expected}",
        )

    def wait_for_symbolic_uds_positive_response(
        self,
        name: str,
        params: str = "{}",
        timeout_s: float | str = "",
        poll_interval_s: float | str = "",
    ) -> Dict[str, Any]:
        resolved_timeout = _resolve_timeout(
            timeout_s, default=self._default_wait_timeout_s
        )
        resolved_poll = _resolve_poll_interval(
            poll_interval_s, default=self._default_wait_poll_interval_s
        )
        return self._wait_until(
            send_fn=lambda: self.send_symbolic_uds_request(name, params),
            condition_fn=lambda resp: bool(resp.get("positive", False)),
            timeout_s=resolved_timeout,
            poll_interval_s=resolved_poll,
            request_label=f"symbolic:{name}",
            expected_label="positive response",
        )

    def wait_for_symbolic_uds_nrc_response(
        self,
        name: str,
        expected_nrc: str,
        params: str = "{}",
        timeout_s: float | str = "",
        poll_interval_s: float | str = "",
    ) -> Dict[str, Any]:
        resolved_timeout = _resolve_timeout(
            timeout_s, default=self._default_wait_timeout_s
        )
        resolved_poll = _resolve_poll_interval(
            poll_interval_s, default=self._default_wait_poll_interval_s
        )
        expected = str(expected_nrc).strip()
        return self._wait_until(
            send_fn=lambda: self.send_symbolic_uds_request(name, params),
            condition_fn=lambda resp: (not bool(resp.get("positive", True)))
            and str(resp.get("nrc")) == expected,
            timeout_s=resolved_timeout,
            poll_interval_s=resolved_poll,
            request_label=f"symbolic:{name}",
            expected_label=f"NRC {expected}",
        )

    def _wait_until(
        self,
        send_fn: Any,
        condition_fn: Any,
        timeout_s: float,
        poll_interval_s: float,
        request_label: str,
        expected_label: str,
    ) -> Dict[str, Any]:
        start = time.perf_counter()
        attempts = 0
        last_response: Dict[str, Any] | None = None

        while True:
            attempts += 1
            response = send_fn()
            last_response = response
            elapsed_s = time.perf_counter() - start
            response["wait_attempts"] = attempts
            response["wait_elapsed_ms"] = elapsed_s * 1000.0
            response["wait_timeout_s"] = timeout_s
            response["wait_poll_interval_s"] = poll_interval_s
            response["wait_expected"] = expected_label
            if condition_fn(response):
                return response

            if elapsed_s >= timeout_s:
                raise AssertionError(
                    "Wait timeout exceeded while waiting for "
                    f'{expected_label} on "{request_label}". '
                    f"attempts={attempts}, elapsed_ms={elapsed_s * 1000.0:.1f}, "
                    f"last_positive={last_response.get('positive')}, "
                    f"last_nrc={last_response.get('nrc')}, "
                    f"last_service={last_response.get('service')}, "
                    f"last_payload={last_response.get('payload')}"
                )

            time.sleep(poll_interval_s)


def _safe_json_object(raw: str) -> Dict[str, Any]:
    """Parse Robot string argument into object with safe fallback."""
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


def _resolve_timeout(value: float | str, default: float) -> float:
    if value in {"", None}:
        return max(default, 0.0)
    return _to_float(value, default=default)


def _resolve_poll_interval(value: float | str, default: float) -> float:
    if value in {"", None}:
        return max(default, 0.01)
    return max(_to_float(value, default=default), 0.01)
