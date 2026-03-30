"""Apply bench ID profiles from JSON to resources/variables/ids.robot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

DEFAULT_PROFILE_DIR = Path("scripts/ids_profiles")
DEFAULT_IDS_FILE = Path("resources/variables/ids.robot")

REQUIRED_KEYS = {
    "ID_PROFILE",
    "CAN_TESTER_PHYSICAL_ID",
    "CAN_ECU_PHYSICAL_ID",
    "CAN_TESTER_FUNCTIONAL_ID",
    "DOIP_TESTER_SOURCE_ADDR",
    "DOIP_ECU_TARGET_ADDR",
    "ECU_LOGICAL_NAME",
    "PROGRAMMING_VARIANT",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply IDs profile to ids.robot.")
    parser.add_argument(
        "--profile-name",
        help="Profile name under scripts/ids_profiles (without .json).",
    )
    parser.add_argument(
        "--profile-file",
        help="Explicit profile JSON path (overrides --profile-name).",
    )
    parser.add_argument("--ids-file", default=str(DEFAULT_IDS_FILE))
    parser.add_argument("--create-backup", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    profile_path = resolve_profile_path(args.profile_name, args.profile_file)
    ids_file = Path(args.ids_file)

    if not ids_file.exists():
        raise FileNotFoundError(f"ids file not found: {ids_file}")

    profile = load_profile(profile_path)
    validate_profile(profile, profile_path)

    updated_text = apply_profile(ids_file.read_text(encoding="utf-8"), profile)

    if args.dry_run:
        print(f"[dry-run] profile={profile_path} ids_file={ids_file}")
        print(updated_text)
        return 0

    if args.create_backup:
        backup = ids_file.with_suffix(ids_file.suffix + ".bak")
        backup.write_text(ids_file.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Backup created: {backup}")

    ids_file.write_text(updated_text, encoding="utf-8")
    print(f"Updated {ids_file} using profile {profile_path.name}")
    return 0


def resolve_profile_path(profile_name: str | None, profile_file: str | None) -> Path:
    if profile_file:
        path = Path(profile_file)
    elif profile_name:
        path = DEFAULT_PROFILE_DIR / f"{profile_name}.json"
    else:
        raise ValueError("Provide either --profile-name or --profile-file.")
    if not path.exists():
        raise FileNotFoundError(f"profile not found: {path}")
    return path


def load_profile(path: Path) -> Dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"profile JSON must be an object: {path}")
    return {str(k): str(v) for k, v in data.items()}


def validate_profile(profile: Dict[str, str], path: Path) -> None:
    missing = sorted(REQUIRED_KEYS - set(profile.keys()))
    if missing:
        raise ValueError(f"profile missing keys in {path}: {', '.join(missing)}")


def apply_profile(ids_robot_text: str, profile: Dict[str, str]) -> str:
    lines = ids_robot_text.splitlines()

    for key, value in profile.items():
        target = "${" + key + "}"
        replacement = f"{target}    {value}"
        replaced = False
        for i, line in enumerate(lines):
            if line.strip().startswith(target):
                lines[i] = replacement
                replaced = True
                break
        if not replaced:
            lines.append(replacement)

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
