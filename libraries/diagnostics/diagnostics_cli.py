"""CLI runner for mock/live diagnostic requests."""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict

from libraries.base.live_preflight import run_live_preflight
from libraries.diagnostics.uds_core import UdsRuntimeConfig, build_client


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one UDS diagnostic request.")
    parser.add_argument("--backend", choices=("mock", "live"), default="mock")
    parser.add_argument("--transport", choices=("can", "doip"), default="can")
    parser.add_argument("--mode", choices=("raw", "symbolic"), default="raw")
    parser.add_argument("--request", default="22 F1 90", help="Raw UDS request payload.")
    parser.add_argument("--name", default="Read_VIN", help="Symbolic diagnostic request name.")
    parser.add_argument("--params", default="{}", help="JSON object string for symbolic params.")
    parser.add_argument(
        "--fixture-path", default="config/fixtures/uds_mock_responses.json", help="Mock fixture path."
    )
    parser.add_argument("--canoe-config-path", default="", help="CANoe configuration file path.")
    parser.add_argument("--auto-measurement", action="store_true", default=False)
    parser.add_argument(
        "--diagnostic-method",
        default="",
        help="Optional method path override, e.g. diagnostics:SendRequest or app:SendDiagnosticRequest.",
    )
    parser.add_argument("--timeout-s", type=float, default=2.0)
    parser.add_argument("--retry-count", type=int, default=1)
    parser.add_argument("--retry-delay-s", type=float, default=0.2)
    parser.add_argument(
        "--preflight-only", action="store_true", help="Run live preflight checks and exit."
    )
    args = parser.parse_args()

    if args.backend == "live":
        preflight = run_live_preflight(args.canoe_config_path)
        print(json.dumps({"preflight": preflight}, indent=2))
        if args.preflight_only or any(value.startswith("fail") for value in preflight.values()):
            return 0 if args.preflight_only else 2
    elif args.preflight_only:
        print(json.dumps({"preflight": {"status": "skip: backend is mock"}}, indent=2))
        return 0

    client = build_client(
        UdsRuntimeConfig(
            backend=args.backend,
            transport=args.transport,
            fixture_path=args.fixture_path,
            canoe_config_path=args.canoe_config_path or None,
            auto_measurement=bool(args.auto_measurement),
            diagnostic_method=args.diagnostic_method or None,
            request_timeout_s=max(args.timeout_s, 0.0),
            retry_count=max(args.retry_count, 0),
            retry_delay_s=max(args.retry_delay_s, 0.0),
        )
    )

    if args.mode == "raw":
        response = client.send_raw(args.request)
    else:
        response = client.send_symbolic(args.name, _parse_params(args.params))

    print(
        json.dumps(
            {
                "service": response.service,
                "payload": response.payload,
                "positive": response.positive,
                "nrc": response.nrc,
                "transport": response.transport,
                "elapsed_ms": response.elapsed_ms,
            },
            indent=2,
        )
    )
    return 0


def _parse_params(raw: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(raw) if raw else {}
    except json.JSONDecodeError as exc:
        raise ValueError("params must be a valid JSON object") from exc
    if not isinstance(parsed, dict):
        raise ValueError("params must be a JSON object")
    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
