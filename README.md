# CANoe Robot Python Automation

ECU validation framework for diagnostics and CAN flashing using Robot Framework, Python, and CANoe.

## Project Description

This project provides:
- Robot test suites for diagnostics and software update flows
- Python libraries for UDS transport/control (`mock` and `live`)
- reusable assertion keywords with clear PASS/FAIL logging
- bench helper scripts for environment and IDs setup

Primary test areas:
- diagnostics: `tests/diagnostics/`
- flashing: `tests/flashing/`

## Setup

### 1) Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 2) Verify local syntax quickly

```bash
python3 -m compileall libraries tests scripts
```

### 3) Run in mock mode (default)

```bash
python3 -m libraries.diagnostics.diagnostics_cli --backend mock --transport can --mode raw --request "22 F1 90"
```

## How To Modify

### Modify test flow
- diagnostics testcases: `tests/diagnostics/positive/`, `tests/diagnostics/negative/`
- flashing testcases: `tests/flashing/positive/`, `tests/flashing/negative/`
- shared Robot keywords: `resources/keywords/`
- runtime variables: `resources/variables/env.robot`, `resources/variables/ids.robot`

### Recommended guides
- test flow updates: `design_docs/Test_Flow_Modification_Guide.md`
- testcase examples + expected PASS/FAIL logs: `design_docs/Testcase_Examples_Pass_Fail.md`
- IDs placeholders and replacement: `design_docs/IDs_Placeholder_Setup_Guide.md`

## How To Use

### Run diagnostics/flashing suites

```bash
python -m robot tests/diagnostics tests/flashing
```

### Check results
- summary: `results/report.html`
- step-by-step details: `results/log.html`
- machine-readable output: `results/output.xml`

### Wait semantics (CAPL-like style)

Diagnostics keywords include explicit wait patterns:
- `Wait For Raw UDS Positive Response`
- `Wait For Raw UDS NRC Response`
- `Wait For Symbolic UDS Positive Response`
- `Wait For Symbolic UDS NRC Response`

### Live bench usage (Windows + CANoe)

Use the runbook:
- `design_docs/Live_Execution_Readiness.md`

Common helper commands:

```powershell
.\scripts\live_env_template.ps1 -CanoeConfigPath "C:\path\to\canoe.cfg" -UdsTransport can -CanoeDiagMethod diagnostics:SendRequest -UdsWaitPollIntervalS 0.2 -CreateBackup
.\scripts\ids_template.ps1 -IdProfile "CAN_BENCH_A" -CanTesterPhysicalId 0x741 -CanEcuPhysicalId 0x749 -CanTesterFunctionalId 0x7DF -CreateBackup
.\scripts\live_gate.ps1 -CanoeConfigPath "C:\path\to\canoe.cfg" -RunRobot
```
