"""CANoe lifecycle wrapper used by live transport adapters."""

from __future__ import annotations

import platform
import re
from pathlib import Path
from typing import Any, Callable, Iterable


class CanoeIntegrationError(RuntimeError):
    """Raised when CANoe integration preconditions are not met."""


class CanoeClient:
    """Thin lifecycle manager for CANoe application sessions."""

    def __init__(
        self,
        config_path: str | None = None,
        auto_measurement: bool = True,
        diagnostic_method: str | None = None,
    ) -> None:
        self.config_path = config_path
        self.auto_measurement = auto_measurement
        self.diagnostic_method = diagnostic_method
        self._connected = False
        self._measuring = False
        self._app: Any | None = None

    def open(self) -> None:
        """Open CANoe COM application and load configuration if provided."""
        self._assert_live_prerequisites()
        self._app = self._dispatch_canoe()

        if self.config_path:
            self._open_configuration(self.config_path)

        self._connected = True
        if self.auto_measurement:
            self.start_measurement()

    def start_measurement(self) -> None:
        """Start CANoe measurement if connected."""
        if not self._connected:
            raise RuntimeError("CANoe is not connected.")
        assert self._app is not None

        measurement = getattr(self._app, "Measurement", None)
        if measurement is None:
            raise CanoeIntegrationError("CANoe COM object does not expose Measurement API.")

        start = getattr(measurement, "Start", None)
        if callable(start):
            start()
            self._measuring = True
            return

        raise CanoeIntegrationError("CANoe Measurement.Start() is unavailable.")

    def stop_measurement(self) -> None:
        """Stop active CANoe measurement."""
        if not self._connected or self._app is None:
            return
        measurement = getattr(self._app, "Measurement", None)
        stop = getattr(measurement, "Stop", None) if measurement is not None else None
        if callable(stop):
            stop()
        self._measuring = False

    def close(self) -> None:
        """Close CANoe session resources."""
        if self._app is not None:
            quit_method = getattr(self._app, "Quit", None)
            if callable(quit_method):
                quit_method()
        self._app = None
        self._connected = False
        self._measuring = False

    def send_diagnostic_request(
        self,
        transport: str,
        mode: str,
        request: str | None = None,
        name: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Send a diagnostic request through the live CANoe session.

        This method uses common method-name fallbacks because COM exposure can differ
        between CANoe configurations and project setups.
        """
        if not self._connected or self._app is None:
            raise CanoeIntegrationError("CANoe client is not open. Call open() first.")

        params = params or {}
        candidates = self._resolve_diagnostic_methods()

        if not candidates:
            raise CanoeIntegrationError(
                "No supported CANoe diagnostic method found. "
                "Verify diagnostic COM access is enabled in your CANoe configuration."
            )

        response = self._invoke_diagnostic_method(
            methods=candidates,
            transport=transport,
            mode=mode,
            request=request,
            name=name,
            params=params,
        )
        service = _resolve_service(mode=mode, request=request, name=name)
        payload = _normalize_payload(str(response))
        nrc = _extract_nrc(payload)

        return {
            "service": service,
            "payload": payload,
            "positive": nrc is None,
            "nrc": nrc,
            "metadata": {"transport": transport, "mode": mode},
        }

    @staticmethod
    def _dispatch_canoe() -> Any:
        try:
            import win32com.client  # type: ignore
        except ImportError as exc:
            raise CanoeIntegrationError(
                "pywin32 is required for live CANoe mode. Install `pywin32` on Windows."
            ) from exc

        try:
            return win32com.client.DispatchEx("CANoe.Application")
        except Exception as exc:  # pragma: no cover - COM exceptions vary by environment
            raise CanoeIntegrationError(
                "Unable to create CANoe COM application. Verify CANoe installation and license."
            ) from exc

    def _open_configuration(self, config_path: str) -> None:
        assert self._app is not None
        cfg = Path(config_path)
        if not cfg.exists():
            raise CanoeIntegrationError(f"CANoe config not found: {cfg}")

        open_candidates = [
            getattr(self._app, "Open", None),
            getattr(getattr(self._app, "Configuration", None), "Open", None),
        ]
        for candidate in open_candidates:
            if callable(candidate):
                candidate(str(cfg.resolve()))
                return

        raise CanoeIntegrationError("Unable to open CANoe configuration via COM API.")

    @staticmethod
    def _assert_live_prerequisites() -> None:
        if platform.system().lower() != "windows":
            raise CanoeIntegrationError("Live CANoe mode requires Windows.")

    def _resolve_diagnostic_methods(self) -> list[Callable[..., Any]]:
        assert self._app is not None
        diagnostics_obj = getattr(self._app, "Diagnostics", None)

        candidates: list[Callable[..., Any]] = []
        if self.diagnostic_method:
            forced = self._method_from_path(self.diagnostic_method)
            if forced is None:
                raise CanoeIntegrationError(
                    f"Configured diagnostic method not found: {self.diagnostic_method}"
                )
            return [forced]

        default_paths = (
            "diagnostics:SendRequest",
            "diagnostics:SendRawRequest",
            "diagnostics:Execute",
            "app:SendDiagnosticRequest",
            "app:SendDiagRequest",
        )
        for method_path in default_paths:
            method = self._method_from_path(method_path, diagnostics_obj=diagnostics_obj)
            if callable(method):
                candidates.append(method)
        return candidates

    def _method_from_path(
        self, method_path: str, diagnostics_obj: Any | None = None
    ) -> Callable[..., Any] | None:
        assert self._app is not None
        diagnostics_obj = diagnostics_obj if diagnostics_obj is not None else getattr(
            self._app, "Diagnostics", None
        )

        try:
            target_hint, method_name = method_path.split(":", 1)
        except ValueError:
            return None

        target_hint = target_hint.strip().lower()
        method_name = method_name.strip()
        if target_hint == "diagnostics" and diagnostics_obj is not None:
            candidate = getattr(diagnostics_obj, method_name, None)
            return candidate if callable(candidate) else None
        if target_hint == "app":
            candidate = getattr(self._app, method_name, None)
            return candidate if callable(candidate) else None
        return None

    @staticmethod
    def _invoke_diagnostic_method(
        methods: Iterable[Callable[..., Any]],
        transport: str,
        mode: str,
        request: str | None,
        name: str | None,
        params: dict[str, Any],
    ) -> Any:
        errors: list[str] = []
        for method in methods:
            try:
                if mode == "raw":
                    for args in (
                        (transport, request),
                        (request,),
                        (request, transport),
                    ):
                        try:
                            return method(*args)
                        except TypeError:
                            continue
                else:
                    for args in (
                        (transport, name, params),
                        (name, params),
                        (transport, name),
                        (name,),
                    ):
                        try:
                            return method(*args)
                        except TypeError:
                            continue
            except Exception as exc:  # pragma: no cover - depends on COM behavior
                method_name = getattr(method, "__name__", repr(method))
                errors.append(f"{method_name}: {exc}")
                continue

        msg = "Unable to invoke CANoe diagnostic method with known signatures."
        if errors:
            msg = f"{msg} Errors: {' | '.join(errors)}"
        raise CanoeIntegrationError(msg)


def _resolve_service(mode: str, request: str | None, name: str | None) -> str:
    if mode == "raw":
        if not request:
            return "unknown"
        return request.strip().split()[0].upper()
    return (name or "unknown").strip()


def _normalize_payload(raw: str) -> str:
    # Normalize only when payload looks like real hex bytes, otherwise keep as-is.
    cleaned = raw.strip()
    if not cleaned:
        return cleaned

    delimited_hex = re.fullmatch(
        r"(?:0x)?[0-9A-Fa-f]{2}(?:[\s,;:-]+(?:0x)?[0-9A-Fa-f]{2})*",
        cleaned,
    )
    compact_hex = re.fullmatch(r"[0-9A-Fa-f]+", cleaned)

    if not delimited_hex and not (compact_hex and len(cleaned) % 2 == 0):
        return cleaned

    pairs = re.findall(r"(?:0x)?([0-9A-Fa-f]{2})", cleaned)
    return " ".join(part.upper() for part in pairs)


def _extract_nrc(payload: str) -> str | None:
    compact = payload.replace(" ", "").upper()
    if not compact.startswith("7F") or len(compact) < 6:
        return None
    # NRC is the third byte in ISO 14229 negative response (7F xx NRC).
    return f"0x{compact[4:6]}"
