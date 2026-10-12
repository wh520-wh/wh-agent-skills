#!/usr/bin/env python3
"""find-planning-files: scan a directory for planning-with-files-zh planning files.

Usage:
  python scripts/find-planning-files.py [<dir>]

Output: JSON to stdout, listing all candidate planning files found.
Behavior: read-only, no side effects.
Exit code: 0 if at least one of task_plan.md/findings.md/progress.md found, 1 otherwise.

Design intent: when an Agent doesn't know where planning files live in a project,
calling this script first is faster, more accurate, and less likely to miss
nested .planning/<plan-id>/ structures than letting the Agent run ls/find itself.

Recognised file names (planning-with-files-zh v3.0.x - v3.1.x):
  task_plan.md, findings.md, progress.md, .active_plan
Recognised directories:
  .attestation/ (v3.1+), .planning/ (nested plan container)

Noise dirs skipped: .git, node_modules, .venv, venv, __pycache__,
                    dist, build, target, .idea, .vscode
"""
import argparse
import json
import os
import sys
from pathlib import Path

KNOWN_FILES = {
    "task_plan.md",
    "findings.md",
    "progress.md",
    ".active_plan",
}
KNOWN_DIRS = {
    ".attestation",
    ".planning",
}
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__",
    "dist", "build", "target", ".idea", ".vscode",
}


def scan(root: Path) -> dict:
    findings = {
        "root": str(root.resolve()),
        "task_plan_files": [],
        "findings_files": [],
        "progress_files": [],
        "active_plan_pointers": [],
        "attestation_dirs": [],
        "planning_containers": [],
    }

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for fname in filenames:
            full = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(full, root).replace(os.sep, "/")
            if fname == "task_plan.md":
                findings["task_plan_files"].append(rel_path)
            elif fname == "findings.md":
                findings["findings_files"].append(rel_path)
            elif fname == "progress.md":
                findings["progress_files"].append(rel_path)
            elif fname == ".active_plan":
                findings["active_plan_pointers"].append(rel_path)

        for dname in list(dirnames):
            full = os.path.join(dirpath, dname)
            rel_path = os.path.relpath(full, root).replace(os.sep, "/")
            if dname == ".attestation":
                findings["attestation_dirs"].append(rel_path)
            elif dname == ".planning":
                findings["planning_containers"].append(rel_path)

    return findings


def main():
    p = argparse.ArgumentParser(
        description="Find planning-with-files-zh planning files in a directory tree (read-only)."
    )
    p.add_argument("path", nargs="?", default=".",
                   help="Root directory (default: current)")
    args = p.parse_args()

    root = Path(args.path)
    if not root.is_dir():
        print(json.dumps({"error": f"Not a directory: {args.path}"},
                         ensure_ascii=False))
        sys.exit(2)

    result = scan(root)
    result["total_planning_files_found"] = (
        len(result["task_plan_files"]) +
        len(result["findings_files"]) +
        len(result["progress_files"])
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["total_planning_files_found"] > 0 else 1)


if __name__ == "__main__":
    main()
