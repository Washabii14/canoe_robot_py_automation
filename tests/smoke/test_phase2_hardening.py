"""Phase 2 hardening smoke checks."""

from __future__ import annotations

from libraries.base.canoe_client import _extract_nrc, _normalize_payload
from libraries.diagnostics.diag_keyword_library import _to_bool


def test_extract_nrc_from_negative_response() -> None:
    assert _extract_nrc("7F 22 31") == "0x31"
    assert _extract_nrc("7F2231") == "0x31"
    assert _extract_nrc("62 F1 90 01") is None


def test_normalize_payload_hex_and_passthrough() -> None:
    assert _normalize_payload("62f190AA") == "62 F1 90 AA"
    assert _normalize_payload("not_hex_payload") == "not_hex_payload"


def test_bool_conversion_for_robot_inputs() -> None:
    assert _to_bool(True) is True
    assert _to_bool("true") is True
    assert _to_bool("False") is False
