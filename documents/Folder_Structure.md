# Folder Structure Guide

This guide explains the project structure for users who need to run, review, or extend the framework.

Use this document as a practical map of where operational files live.

## 1. Objective

Use this guide to quickly find:
- setup and usage documentation
- runtime configuration files
- Python libraries and Robot resources
- test suites and helper scripts

## 2. Folder Structure

```text
canoe_robot_py_automation/
├── config/
│   ├── canoe_env/                    # CANoe config placeholders and runtime pointers
│   ├── diagnostics/                  # CDD/ODX placeholders
│   └── fixtures/                     # Offline request/response fixtures for mock tests
├── documents/
│   ├── Folder_Structure.md           # This file
│   ├── Getting_Started.md            # Setup and first local run
│   ├── Live_Bench_Usage.md           # Windows bench execution steps
│   └── Test_Authoring_Guide.md       # How to write and update tests
├── scripts/
│   ├── live_gate.py                  # Live preflight + optional Robot live run
│   ├── live_gate.ps1                 # Windows PowerShell live gate runner
│   ├── live_gate.bat                 # Windows batch live gate runner
│   ├── live_env_template.ps1         # Update env.robot for live execution
│   ├── live_env_template.bat         # Batch wrapper for env updates
│   ├── ids_template.ps1              # Update ids.robot with direct values
│   ├── ids_template.bat              # Batch wrapper for ID updates
│   ├── ids_profile_apply.py          # Apply ids.robot values from a named profile
│   └── ids_profiles/
│       ├── can_bench_a.json          # Sample CAN bench profile
│       └── doip_bench_b.json         # Sample DoIP bench profile
├── libraries/
│   ├── base/
│   │   ├── canoe_client.py           # CANoe lifecycle helper
│   │   ├── live_preflight.py         # Live readiness checks
│   │   └── transport_interface.py    # Shared transport contract
│   ├── diagnostics/
│   │   ├── diag_keyword_library.py   # Robot-facing diagnostics keywords
│   │   ├── diagnostics_cli.py        # CLI entrypoint for UDS requests
│   │   ├── uds_core.py               # Transport-agnostic request/response flow
│   │   ├── uds_can.py                # CAN/CAN-FD adapter
│   │   ├── uds_doip.py               # DoIP adapter
│   │   └── uds_mock.py               # Offline deterministic adapter
│   └── software_update/
│       ├── flash_core.py             # Shared flashing state machine
│       ├── flash_can.py              # CAN flashing sequence
│       └── flash_keyword_library.py  # Robot-facing flashing keywords
├── resources/
│   ├── keywords/
│   │   ├── assertion_keywords.robot  # Shared PASS/FAIL assertions
│   │   ├── diag_keywords.robot       # Diagnostics keywords
│   │   └── flash_keywords.robot      # Flashing keywords
│   └── variables/
│       ├── env.robot                 # Backend and runtime settings
│       └── ids.robot                 # Tester/ECU IDs and addressing defaults
├── tests/
│   ├── diagnostics/
│   │   ├── positive/                 # Positive diagnostics Robot suites
│   │   └── negative/                 # Negative diagnostics Robot suites
│   ├── flashing/
│   │   ├── positive/                 # Positive flashing Robot suites
│   │   └── negative/                 # Negative flashing Robot suites
│   └── smoke/
│       └── test_*.py                 # Python smoke checks for contracts, adapters, flashing, abstraction, and waits
├── .github/
│   └── workflows/
│       └── ci.yml                    # CI checks for compile, smoke, and Robot dry-run
├── results/                          # Generated Robot reports and logs
├── README.md                         # Project overview
├── requirements.txt                  # Third-party Python dependencies
└── pyproject.toml                    # Editable package metadata
```

## 3. What To Open For Common Tasks

- First-time setup: `documents/Getting_Started.md`
- Understand the repo layout: `documents/Folder_Structure.md`
- Write or update testcases: `documents/Test_Authoring_Guide.md`
- Prepare a Windows bench run: `documents/Live_Bench_Usage.md`
- Change runtime settings: `resources/variables/env.robot`
- Update bench IDs: `resources/variables/ids.robot` or `scripts/ids_profile_apply.py`

## 4. Notes

- `libraries/` contains the Python implementation used by CLI tools, smoke tests, and Robot-facing keyword libraries.
- `resources/keywords/` and `resources/variables/` are the main Robot Framework integration points.
- `config/fixtures/` supports CI-safe and local mock validation without requiring CANoe hardware access.
- `tests/diagnostics/negative` and `tests/flashing/negative` are for negative-path validation and error handling coverage.
- `results/` is generated after Robot runs and contains the main execution evidence.
