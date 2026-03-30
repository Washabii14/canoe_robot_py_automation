"""Phase 5 smoke checks for Robot abstraction libraries."""

from __future__ import annotations

import json

from libraries.diagnostics.diag_keyword_library import DiagKeywordLibrary
from libraries.software_update.flash_keyword_library import FlashKeywordLibrary


def test_diag_keyword_library_mock_call() -> None:
    lib = DiagKeywordLibrary(
        backend="mock",
        transport="can",
        fixture_path="config/fixtures/uds_mock_responses.json",
    )
    response = lib.send_raw_uds_request("22 F1 90")
    assert response["positive"] is True
    assert response["service"] == "0x22"


def test_flash_keyword_library_mock_flow_and_verify() -> None:
    lib = FlashKeywordLibrary(
        backend="mock",
        transport="can",
        fixture_path="config/fixtures/uds_mock_responses.json",
    )
    result = lib.start_can_flashing(json.dumps({}))
    assert result["success"] is True

    verified = lib.verify_flashing_result(True)
    assert verified["success"] is True
