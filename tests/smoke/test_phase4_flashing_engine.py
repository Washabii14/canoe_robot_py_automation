"""Phase 4 smoke checks for CAN flashing engine."""

from __future__ import annotations

from collections import defaultdict

from libraries.diagnostics.uds_core import UdsResponse
from libraries.software_update.flash_can import CanFlasher


class _FakeUdsClient:
    def __init__(self, scripted: dict[str, list[UdsResponse] | Exception]) -> None:
        self.scripted = scripted
        self.counts: dict[str, int] = defaultdict(int)

    def send_raw(self, bytes_req: str) -> UdsResponse:
        key = bytes_req.strip()
        if key not in self.scripted:
            return UdsResponse(
                service="unknown",
                payload="",
                positive=False,
                nrc="0x31",
                transport="can",
                elapsed_ms=0.0,
            )
        scripted_item = self.scripted[key]
        if isinstance(scripted_item, Exception):
            raise scripted_item
        idx = self.counts[key]
        self.counts[key] += 1
        if idx >= len(scripted_item):
            return scripted_item[-1]
        return scripted_item[idx]


def _pos(service: str) -> UdsResponse:
    return UdsResponse(
        service=service,
        payload="ok",
        positive=True,
        nrc=None,
        transport="can",
        elapsed_ms=0.1,
    )


def _neg(service: str, nrc: str) -> UdsResponse:
    return UdsResponse(
        service=service,
        payload=f"7F {service} {nrc}",
        positive=False,
        nrc=nrc,
        transport="can",
        elapsed_ms=0.1,
    )


def test_flashing_positive_path_completes() -> None:
    fake = _FakeUdsClient(
        {
            "10 02": [_pos("0x10")],
            "27 01": [_pos("0x27")],
            "27 02 11 22 33 44": [_pos("0x27")],
            "34 00 44 00 00 00 20": [_pos("0x34")],
            "36 01 AA BB": [_pos("0x36")],
            "36 02 CC DD": [_pos("0x36")],
            "37": [_pos("0x37")],
        }
    )
    flasher = CanFlasher(fake)
    result = flasher.start(
        {
            "security_key": "11 22 33 44",
            "request_download": "34 00 44 00 00 00 20",
            "transfer_blocks": ["AA BB", "CC DD"],
        }
    )
    assert result.success is True
    assert result.step == "complete"
    assert result.aborted is False


def test_flashing_wrong_block_sequence_triggers_abort() -> None:
    fake = _FakeUdsClient(
        {
            "10 02": [_pos("0x10")],
            "27 01": [_pos("0x27")],
            "27 02 11 22 33 44": [_pos("0x27")],
            "34 00 44 00 00 00 20": [_pos("0x34")],
            "36 01 AA BB": [_neg("0x36", "0x73")],
            "11 01": [_pos("0x11")],
        }
    )
    flasher = CanFlasher(fake)
    result = flasher.start(
        {
            "security_key": "11 22 33 44",
            "request_download": "34 00 44 00 00 00 20",
            "transfer_blocks": ["AA BB"],
        }
    )
    assert result.success is False
    assert result.aborted is True
    assert "Wrong block sequence" in result.reason


def test_flashing_timeout_triggers_controlled_abort() -> None:
    fake = _FakeUdsClient(
        {
            "10 02": TimeoutError("session timeout"),
            "11 01": [_pos("0x11")],
        }
    )
    flasher = CanFlasher(fake)
    result = flasher.start({"transfer_blocks": ["AA"]})
    assert result.success is False
    assert result.aborted is True
    assert "timeout" in result.reason.lower()
