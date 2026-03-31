# Getting Started

This framework supports ECU diagnostics and CAN flashing using Robot Framework + Python + CANoe.

## Prerequisites

- Python 3.9+
- Robot Framework
- (Live bench) Windows + CANoe + Vector hardware + `pywin32`

Install dependencies and the editable project package:

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

The editable install keeps `libraries` imports stable for CLI commands, smoke tests, and IDE/local runs.

Run Python smoke tests:

```bash
python3 -m pytest -q tests/smoke
```

## Run In Mock Mode

Quick command:

```bash
python3 -m libraries.diagnostics.diagnostics_cli --backend mock --transport can --mode raw --request "22 F1 90"
```

Run Robot tests:

```bash
python -m robot tests/diagnostics tests/flashing
```

Results are generated in:
- `results/report.html`
- `results/log.html`
- `results/output.xml`

## Edit Tests

- Diagnostics tests:
  - `tests/diagnostics/positive/`
  - `tests/diagnostics/negative/`
- Flashing tests:
  - `tests/flashing/positive/`
  - `tests/flashing/negative/`

Reusable keywords:
- `resources/keywords/diag_keywords.robot`
- `resources/keywords/flash_keywords.robot`
- `resources/keywords/assertion_keywords.robot`

## CAPL-like Wait Semantics

Diagnostics supports explicit wait-until-timeout style keywords:
- `Wait For Raw UDS Positive Response`
- `Wait For Raw UDS NRC Response`
- `Wait For Symbolic UDS Positive Response`
- `Wait For Symbolic UDS NRC Response`
