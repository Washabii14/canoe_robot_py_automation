"""Phase 7 live gate helper: preflight + optional live Robot run."""

from __future__ import annotations

import argparse
import subprocess
import sys

from libraries.base.live_preflight import run_live_preflight


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live readiness gate checks.")
    parser.add_argument("--canoe-config-path", required=True)
    parser.add_argument("--run-robot", action="store_true")
    parser.add_argument(
        "--robot-path", default="robot", help="Robot executable name/path in active environment."
    )
    args = parser.parse_args()

    preflight = run_live_preflight(args.canoe_config_path)
    for key, value in preflight.items():
        print(f"{key}: {value}")

    if any(str(value).startswith("fail") for value in preflight.values()):
        return 2

    if not args.run_robot:
        return 0

    cmd = [args.robot_path, "tests/diagnostics", "tests/flashing"]
    proc = subprocess.run(cmd, check=False)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
