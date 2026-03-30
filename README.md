# CANoe Robot Python Automation

Offline-first ECU validation framework for diagnostics and CAN flashing using Robot Framework + Python + CANoe.

## Quick Start (Mock)

```bash
python3 -m pip install -r requirements.txt
python3 -m libraries.diagnostics.diagnostics_cli --backend mock --transport can --mode raw --request "22 F1 90"
python3 -m compileall libraries tests
```

Diagnostics wait semantics (CAPL-like style) are available via Robot keywords:
- `Wait For Raw UDS Positive Response`
- `Wait For Raw UDS NRC Response`
- `Wait For Symbolic UDS Positive Response`
- `Wait For Symbolic UDS NRC Response`

## CI Checks

CI workflow at `.github/workflows/ci.yml` runs:
- syntax compilation
- smoke tests (`tests/smoke`)
- Robot dry-run on diagnostics/flashing suites

## Live Readiness (Phase 7)

Use:
- `design_docs/Live_Execution_Readiness.md` for step-by-step checklist and commands
- `scripts/live_gate.py` for executable preflight and optional live Robot run
- `scripts/live_gate.ps1` and `scripts/live_gate.bat` for one-command Windows execution
- `scripts/live_env_template.ps1` and `scripts/live_env_template.bat` to update `resources/variables/env.robot` for live mode
- `scripts/ids_template.ps1` and `scripts/ids_template.bat` to update `resources/variables/ids.robot` bench IDs
- `scripts/ids_profile_apply.py` + `scripts/ids_profiles/*.json` for profile-name based IDs updates

Example (Windows):

```bash
python -m scripts.live_gate --canoe-config-path "C:\\path\\to\\canoe.cfg"
python -m scripts.live_gate --canoe-config-path "C:\\path\\to\\canoe.cfg" --run-robot
```

PowerShell one-command:

```powershell
.\scripts\live_gate.ps1 -CanoeConfigPath "C:\path\to\canoe.cfg" -RunRobot
```

Batch one-command:

```bat
scripts\live_gate.bat "C:\path\to\canoe.cfg" --run-robot
```

Environment template update:

```powershell
.\scripts\live_env_template.ps1 -CanoeConfigPath "C:\path\to\canoe.cfg" -UdsTransport can -CanoeDiagMethod diagnostics:SendRequest -UdsWaitPollIntervalS 0.2 -CreateBackup
```

IDs template update:

```powershell
.\scripts\ids_template.ps1 -IdProfile "CAN_BENCH_A" -CanTesterPhysicalId 0x741 -CanEcuPhysicalId 0x749 -CanTesterFunctionalId 0x7DF -CreateBackup
```

IDs profile update:

```bash
python -m scripts.ids_profile_apply --profile-name can_bench_a --create-backup
python -m scripts.ids_profile_apply --profile-name doip_bench_b --create-backup
```
