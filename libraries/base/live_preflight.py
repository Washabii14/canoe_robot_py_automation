"""Preflight checks for live CANoe execution."""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Dict


def run_live_preflight(canoe_config_path: str) -> Dict[str, str]:
    """Return a status map for live execution readiness checks."""
    status: Dict[str, str] = {}

    if platform.system().lower() != "windows":
        status["os"] = "fail: live CANoe mode requires Windows"
    else:
        status["os"] = "ok"

    cfg = Path(canoe_config_path)
    status["canoe_config"] = "ok" if cfg.exists() else f"fail: missing {cfg}"

    try:
        import win32com.client  # type: ignore

        _ = win32com.client
        status["pywin32"] = "ok"
    except ImportError:
        status["pywin32"] = "fail: install pywin32 in active Python environment"

    return status
