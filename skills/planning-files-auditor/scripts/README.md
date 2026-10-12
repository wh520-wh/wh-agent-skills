# scripts/

Read-only helper scripts for `planning-files-auditor`.

All scripts here follow the skill's hard boundary: **no file writes, no source modifications, no external network calls**. They exist to make the Agent's job faster/more accurate when reading planning files.

## Inventory

| Script | Purpose | Side effects |
|---|---|---|
| `find-planning-files.py` | Scan a directory tree for `task_plan.md` / `findings.md` / `progress.md` / `.active_plan` / `.attestation/` / `.planning/` | Read-only |

## Usage

```bash
python scripts/find-planning-files.py            # scan current dir
python scripts/find-planning-files.py path/to/project
```

Output is JSON to stdout. Exit code:
- `0` — at least one of `task_plan.md` / `findings.md` / `progress.md` found
- `1` — none found
- `2` — error (e.g. path not a directory)

## When the skill calls these

The skill's `## 输入和范围` section says:
> 在当前项目中查找活动的 planning-with-files-zh 位置,包括根目录规划文件和 `.planning/<plan-id>/` 结构。

The Agent should run `find-planning-files.py` first to enumerate candidates, then ask the user (in Chinese) which to audit when multiple groups are found.

## Adding new scripts

New scripts must:
1. Be **read-only** — no `open(..., 'w')`, no `os.remove`, no `subprocess` that mutates.
2. Be **zero-dependency** — Python stdlib only, no `pip install`.
3. Output **machine-readable** (JSON preferred) when an Agent will consume the output.
4. Be documented in this README inventory.

Anything that touches files or makes network calls belongs outside this directory.
