"""
Renames DIGSOL submission files inside per-student subfolders.

Each subfolder under the given root directory is expected to be named
"Surname, Firstname". Within each subfolder:
  - .mov files are renamed to  DIGSOL_Video_Response_<Surname>_<Firstname>.mov
  - .docx files are renamed to DIGSOL_Folio_Response_<Surname>_<Firstname>.docx

If a folder has more than one file of a given type, extras get a numeric
suffix (_2, _3, ...) so nothing is overwritten.

Usage:
    python rename_digsol_files.py /path/to/root [--dry-run]
"""

import argparse
import sys
from pathlib import Path

EXTENSION_PREFIXES = {
    ".mov": "DIGSOL_Video_Response",
    ".docx": "DIGSOL_Folio_Response",
}


def parse_folder_name(folder_name: str) -> tuple[str, str] | None:
    """Split 'Surname, Firstname' into (surname, firstname). Returns None if malformed."""
    if "," not in folder_name:
        return None
    surname, _, firstname = folder_name.partition(",")
    surname = surname.strip()
    firstname = firstname.strip()
    if not surname or not firstname:
        return None
    return surname, firstname


def unique_target(folder: Path, base_name: str, suffix: str) -> Path:
    """Return a non-colliding path for base_name+suffix inside folder, adding _2, _3, ... if needed."""
    candidate = folder / f"{base_name}{suffix}"
    n = 2
    while candidate.exists():
        candidate = folder / f"{base_name}_{n}{suffix}"
        n += 1
    return candidate


def rename_files_in_folder(folder: Path, dry_run: bool) -> None:
    parsed = parse_folder_name(folder.name)
    if parsed is None:
        print(f"Skipping '{folder.name}': expected folder name format 'Surname, Firstname'")
        return
    surname, firstname = parsed

    for file_path in sorted(folder.iterdir()):
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()
        prefix = EXTENSION_PREFIXES.get(suffix)
        if prefix is None:
            continue

        base_name = f"{prefix}_{surname}_{firstname}"
        if file_path.stem == base_name and suffix == file_path.suffix:
            print(f"'{file_path.name}' already has target name, skipping")
            continue

        new_path = unique_target(folder, base_name, suffix)

        action = "[DRY RUN] " if dry_run else ""
        print(f"{action}Renaming '{file_path.name}' -> '{new_path.name}' (in {folder.name})")
        if not dry_run:
            file_path.rename(new_path)


def main():
    parser = argparse.ArgumentParser(
        description="Rename DIGSOL video/folio response files based on student subfolder names."
    )
    parser.add_argument("root", type=Path, help="Root directory containing 'Surname, Firstname' subfolders")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be renamed without renaming")
    args = parser.parse_args()

    if not args.root.is_dir():
        sys.exit(f"Error: '{args.root}' is not a directory")

    subfolders = [p for p in sorted(args.root.iterdir()) if p.is_dir()]
    if not subfolders:
        sys.exit(f"No subfolders found in '{args.root}'")

    for folder in subfolders:
        rename_files_in_folder(folder, args.dry_run)


if __name__ == "__main__":
    main()
