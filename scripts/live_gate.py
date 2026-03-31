"""Live bench preflight helper with optional Robot execution."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from libraries.base.live_preflight import run_live_preflight

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live readiness gate checks.")
    parser.add_argument("--canoe-config-path", required=True)
    parser.add_argument("--run-robot", action="store_true")
    parser.add_argument(
        "--robot-path",
        default="",
        help="Optional Robot executable override. Defaults to `python -m robot`.",
    )
    args = parser.parse_args()

    preflight = run_live_preflight(args.canoe_config_path)
    for key, value in preflight.items():
        print(f"{key}: {value}")

    if any(str(value).startswith("fail") for value in preflight.values()):
        return 2

    if not args.run_robot:
        return 0

    diagnostics_suite = str(REPO_ROOT / "tests" / "diagnostics")
    flashing_suite = str(REPO_ROOT / "tests" / "flashing")
    cmd = (
        [args.robot_path, diagnostics_suite, flashing_suite]
        if args.robot_path
        else [sys.executable, "-m", "robot", diagnostics_suite, flashing_suite]
    )
    proc = subprocess.run(cmd, check=False, cwd=str(REPO_ROOT))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
