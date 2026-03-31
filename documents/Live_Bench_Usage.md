# Live Bench Usage

Use this guide on a Windows bench with CANoe and hardware available.

Before using these steps:
- complete the Python setup from `documents/Getting_Started.md`
- open Windows PowerShell in the repository root

## 1. Configure Runtime Variables

Set the live runtime values in `resources/variables/env.robot` with the helper script:

```powershell
.\scripts\live_env_template.ps1 -CanoeConfigPath "C:\path\to\canoe.cfg" -UdsTransport can -CanoeDiagMethod diagnostics:SendRequest -UdsWaitPollIntervalS 0.2 -CreateBackup
```

This updates the execution backend, CANoe config path, transport, diagnostic method, and wait timing for live use.

## 2. Apply Bench IDs

Use one of the following approaches to update `resources/variables/ids.robot`.

Option A: profile-based update

```powershell
python -m scripts.ids_profile_apply --profile-name can_bench_a --create-backup
```

Option B: direct values

```powershell
.\scripts\ids_template.ps1 -IdProfile "CAN_BENCH_A" -CanTesterPhysicalId "0x741" -CanEcuPhysicalId "0x749" -CanTesterFunctionalId "0x7DF" -CreateBackup
```

Use values that match the real bench configuration before continuing.

## 3. Run Preflight And Tests

```powershell
.\scripts\live_gate.ps1 -CanoeConfigPath "C:\path\to\canoe.cfg" -RunRobot
```

The live gate wrapper prepares the active Python environment before execution:
- install dependencies from `requirements.txt`
- install `pywin32` automatically if it is missing
- install the editable project package with `pip install -e .`

It then runs the live preflight and, if requested, the Robot diagnostics and flashing suites.

## 4. Verify Outputs

After execution, check:
- `results/report.html`
- `results/log.html`
- `results/output.xml`
