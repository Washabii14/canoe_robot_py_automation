# Live Bench Usage

Use this on Windows bench with CANoe and hardware available.

## 1) Configure Runtime Variables

Update live environment in one command:

```powershell
.\scripts\live_env_template.ps1 -CanoeConfigPath "C:\path\to\canoe.cfg" -UdsTransport can -CanoeDiagMethod diagnostics:SendRequest -UdsWaitPollIntervalS 0.2 -CreateBackup
```

## 2) Apply Bench IDs

Option A: profile-based (recommended)

```bash
python -m scripts.ids_profile_apply --profile-name can_bench_a --create-backup
```

Option B: direct values

```powershell
.\scripts\ids_template.ps1 -IdProfile "CAN_BENCH_A" -CanTesterPhysicalId 0x741 -CanEcuPhysicalId 0x749 -CanTesterFunctionalId 0x7DF -CreateBackup
```

## 3) Run Preflight + Tests

```powershell
.\scripts\live_gate.ps1 -CanoeConfigPath "C:\path\to\canoe.cfg" -RunRobot
```

## 4) Verify Outputs

Check:
- `results/report.html`
- `results/log.html`
- `results/output.xml`
