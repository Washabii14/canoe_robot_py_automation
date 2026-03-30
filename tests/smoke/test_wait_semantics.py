"""Smoke checks for CAPL-like wait semantics in diagnostics keywords."""

from __future__ import annotations

import pytest

from libraries.diagnostics.diag_keyword_library import DiagKeywordLibrary


def test_wait_for_raw_positive_response_returns_with_wait_metadata() -> None:
    lib = DiagKeywordLibrary(
        backend="mock",
        transport="can",
        fixture_path="config/fixtures/uds_mock_responses.json",
    )
    result = lib.wait_for_raw_uds_positive_response("22 F1 90", timeout_s=0.5, poll_interval_s=0.05)

    assert result["positive"] is True
    assert result["wait_attempts"] >= 1
    assert result["wait_elapsed_ms"] >= 0.0
    assert result["wait_expected"] == "positive response"


def test_wait_for_raw_nrc_response_times_out_with_clear_message() -> None:
    lib = DiagKeywordLibrary(
        backend="mock",
        transport="can",
        fixture_path="config/fixtures/uds_mock_responses.json",
    )

    with pytest.raises(AssertionError) as exc:
        lib.wait_for_raw_uds_nrc_response(
            "22 F1 90",
            expected_nrc="0x13",
            timeout_s=0.05,
            poll_interval_s=0.01,
        )

    assert "Wait timeout exceeded" in str(exc.value)
    assert "NRC 0x13" in str(exc.value)
