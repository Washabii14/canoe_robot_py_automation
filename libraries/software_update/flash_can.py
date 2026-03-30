"""CAN-specific flashing sequence implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from libraries.diagnostics.uds_core import UdsResponse
from libraries.software_update.flash_core import FlashResult, FlashStateMachine


class UdsLikeClient(Protocol):
    def send_raw(self, bytes_req: str) -> UdsResponse: ...


@dataclass
class FlashPlan:
    security_key: str
    request_download: str
    transfer_blocks: List[str]
    transfer_exit: str = "37"
    abort_request: str = "11 01"


class CanFlasher:
    """CAN flashing wrapper around the shared flash state machine."""

    def __init__(self, uds_client: UdsLikeClient) -> None:
        self.uds_client = uds_client
        self.state_machine = FlashStateMachine()

    def start(self, image_meta: dict) -> FlashResult:
        """Execute CAN flashing flow with controlled abort on failure."""
        plan = _build_plan(image_meta)
        try:
            self.state_machine.advance("session")
            self._send_and_expect("10 02", expected_service="0x10", step_name="session")

            self.state_machine.advance("security_seed")
            self._send_and_expect("27 01", expected_service="0x27", step_name="security_seed")

            self.state_machine.advance("security_key")
            self._send_and_expect(
                f"27 02 {plan.security_key}",
                expected_service="0x27",
                step_name="security_key",
            )

            self.state_machine.advance("download")
            self._send_and_expect(
                plan.request_download, expected_service="0x34", step_name="download"
            )

            self.state_machine.advance("transfer")
            for index, block in enumerate(plan.transfer_blocks, start=1):
                request = f"36 {index:02X} {block}".strip()
                response = self.uds_client.send_raw(request)
                if response.nrc == "0x73":
                    raise RuntimeError(f"Wrong block sequence at index {index}")
                if not response.positive:
                    raise RuntimeError(
                        f"Transfer failed at block {index} with NRC={response.nrc or 'unknown'}"
                    )
                if response.service not in {"0x36", "36"}:
                    raise RuntimeError(
                        f"Unexpected transfer response service {response.service} at block {index}"
                    )

            self.state_machine.advance("transfer_exit")
            self._send_and_expect(
                plan.transfer_exit, expected_service="0x37", step_name="transfer_exit"
            )

            self.state_machine.advance("complete")
            return self.state_machine.success()
        except (TimeoutError, RuntimeError, ValueError) as exc:
            aborted = self._attempt_controlled_abort(plan.abort_request)
            return self.state_machine.fail(reason=str(exc), aborted=aborted)

    def _send_and_expect(self, request: str, expected_service: str, step_name: str) -> None:
        response = self.uds_client.send_raw(request)
        if not response.positive:
            raise RuntimeError(
                f"{step_name} failed with NRC={response.nrc or 'unknown'} for request {request}"
            )
        if response.service not in {expected_service, expected_service.replace("0x", "")}:
            raise RuntimeError(
                f"{step_name} unexpected service {response.service}, expected {expected_service}"
            )

    def _attempt_controlled_abort(self, abort_request: str) -> bool:
        try:
            response = self.uds_client.send_raw(abort_request)
            return bool(response.positive)
        except Exception:
            return False


def _build_plan(image_meta: dict) -> FlashPlan:
    key = str(image_meta.get("security_key", "00 00 00 00")).strip()
    download = str(image_meta.get("request_download", "34 00 44 00 00 00 10")).strip()
    blocks = image_meta.get("transfer_blocks", ["DE AD BE EF"])

    if not isinstance(blocks, list) or not blocks:
        raise ValueError("transfer_blocks must be a non-empty list")

    normalized_blocks = [str(block).strip() for block in blocks if str(block).strip()]
    if not normalized_blocks:
        raise ValueError("transfer_blocks contains no valid payloads")

    return FlashPlan(
        security_key=key,
        request_download=download,
        transfer_blocks=normalized_blocks,
        transfer_exit=str(image_meta.get("transfer_exit", "37")).strip(),
        abort_request=str(image_meta.get("abort_request", "11 01")).strip(),
    )
