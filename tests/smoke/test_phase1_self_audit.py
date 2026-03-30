"""Phase 1 smoke checks for contracts and mock flow."""

from __future__ import annotations

from libraries.diagnostics.uds_core import UdsRuntimeConfig, build_client


def test_mock_raw_request_returns_normalized_response() -> None:
    client = build_client(
        UdsRuntimeConfig(
            backend="mock",
            transport="can",
            fixture_path="config/fixtures/uds_mock_responses.json",
        )
    )
    response = client.send_raw("22 F1 90")

    assert response.service == "0x22"
    assert response.positive is True
    assert response.transport == "can"
    assert response.elapsed_ms >= 0.0


def test_mock_symbolic_request_returns_normalized_response() -> None:
    client = build_client(
        UdsRuntimeConfig(
            backend="mock",
            transport="doip",
            fixture_path="config/fixtures/uds_mock_responses.json",
        )
    )
    response = client.send_symbolic("Read_VIN")

    assert response.service == "Read_VIN"
    assert response.positive is True
    assert response.transport == "doip"
