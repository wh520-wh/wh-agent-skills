---
name: Prune-cc
description: >
  Completely and safely remove (uninstall / delete / prune) a Claude Code plugin, skill, or marketplace
  AND everything attached to it — cache files, marketplace source, symlink targets, the real skill
  folder under ~/.agents/skills, settings.json marketplace registration, settings.local.json
  enabledPlugins entries, and .skill-lock.json records. Use this whenever the user wants to remove,
  uninstall, delete, clean up, get rid of, wipe, or prune ANY plugin, skill, agent, marketplace, or
  "that thing I installed" from Claude Code — globally so no project loads it again. Trigger on words
  like remove, uninstall, delete, 卸载, 删除, 清理, 清除, 卸掉, 干掉, 抹掉, prune, clean up, wipe,
  get rid of, take off, 以及"把xxx插件/skill删干净""全局删除""所有项目都不再加载". Do NOT skip this
  skill for "just remove X" requests — safe removal requires investigating where the thing actually
  lives first, because Claude Code stores the same logical plugin in up to four separate places and
  many skill names are shared between unrelated sources.
---

# Prune-cc — Safely & Completely Remove a Claude Code Plugin or Skill

> **Designed exclusively for Claude Code.** Every path, command, and mechanism below is specific to
> the Claude Code CLI (~/.claude/, ~/.agents/, /plugin, settings.json, .skill-lock.json).
> It does not apply to Cursor, Codex, Cline, or other harnesses without adaptation.

## Why this skill exists

Removing a Claude Code plugin or skill is **not** `rm -rf one-folder`. The same logical thing is often
stored in **up to four separate places**, and several popular skill names (`tdd`, `diagnosing-bugs`,
`codebase-design`, `prototype`, `handoff` …) are shipped by **multiple unrelated sources**. A careless
delete wipes the wrong skill, leaves broken symlinks, or leaves stale config that keeps reloading the
thing you thought you removed.

This skill turns removal into a safe, deterministic, **investigate-then-delete** procedure. The whole
point: figure out exactly where the target lives and which source it belongs to *before* deleting
anything, and stop to ask the user when the source is ambiguous.

## The two storage models — read this first

Claude Code installs things in one of two completely different ways. You must identify which one
applies before touching anything.

### Model A — Marketplace plugin (installed via `/plugin`)

Lives in up to four places:

| # | Location | What it is |
|---|----------|-----------|
| 1 | `~/.claude/plugins/cache/<marketplace>/...` | Installed/cached plugin files |
| 2 | `~/.claude/plugins/marketplaces/<marketplace>/...` | Marketplace source clone |
| 3 | `~/.claude/settings.json` → `extraKnownMarketplaces.<marketplace>` | Marketplace registration |
| 4 | `~/.claude/settings.local.json` → `enabledPlugins."<plugin>@<marketplace>"` | Per-install enable flag |

Example: a marketplace named `ecc` shows up as `plugins/cache/ecc/`, `plugins/marketplaces/ecc/`,
`settings.json` `extraKnownMarketplaces.ecc`, and `settings.local.json` `enabledPlugins."ecc@ecc"`.

### Model B — User-level skill (installed by a skill-installer like `setup-matt-pocock-skills`)

Lives in **three** places. The skill you see in `~/.claude/skills/<name>` is **either a symlink
into `~/.agents/skills/` or a real directory** — do not assume. On the same machine some entries
are symlinks (`luban`, `obsidian-vault`) while others are plain folders (`ppt-master`, `Prune-cc`),
because different installers and different OSes behave differently. **Always `test -L` first**
(see 1.4) and branch on the result:

| # | Location | What it is |
|---|----------|-----------|
| 1 | `~/.claude/skills/<name>` | The visible skill — a **symlink** into `~/.agents/skills/` (may show `@` in `ls -la`), OR a **real directory** if the installer copied instead of linking |
| 2 | `~/.agents/skills/<name>` | The REAL folder (the symlink target, if #1 is a symlink). May itself be a symlink pointing elsewhere — see 1.4 |
| 3 | `~/.agents/.skill-lock.json` | Manifest: `skills.<name>` records `source` (e.g. `mattpocock/skills`) and `sourceUrl`. **Not every on-disk skill is listed here** — user-installed ones often aren't |

This model is the dangerous one: `~/.agents/skills/` is a **shared** folder mixing skills from many
sources (the user's own `luban`, `ppt-master`, etc. sit next to `mattpocock` skills). Never
`rm -rf ~/.agents/skills/` wholesale — you'd destroy the user's own skills.

## Phase 1 — INVESTIGATE (read-only, do not delete yet)

Run every check below before deleting anything. These are all safe read commands.

### 1.1 List installed marketplaces and plugins

```bash
echo "=== marketplaces ==="
ls -1 ~/.claude/plugins/marketplaces/ 2>/dev/null
echo "=== cache ==="
ls -1 ~/.claude/plugins/cache/ 2>/dev/null
```

### 1.2 Find each marketplace's real name and source URL

```bash
for f in ~/.claude/plugins/marketplaces/*/.claude-plugin/marketplace.json; do
  echo "--- $f ---"
  grep -iE '"name"|"url"' "$f" 2>/dev/null | head -5
done
```

This tells you the registered marketplace name and author/URL — use it to match the user's target
("delete the Matt Pocock one") to the right folder.

### 1.3 Check settings for registrations and enable flags

Read `~/.claude/settings.json` (look for `extraKnownMarketplaces`) and
`~/.claude/settings.local.json` (look for `enabledPlugins`). Note any entry tied to the target.

### 1.4 For Model B skills — resolve symlinks and read the manifest

First decide whether the visible skill is a symlink or a real folder, then find the REAL folder:

```bash
name=<name>
if [ -L ~/.claude/skills/$name ]; then
  echo "visible = SYMLINK -> $(readlink ~/.claude/skills/$name)"   # target is the real folder
else
  echo "visible = REAL DIRECTORY (installer copied, not linked)"    # this folder IS the real one
fi

# The target under ~/.agents/skills/ may ITSELF be a symlink (e.g. netease-uu-booster ->
# ~/AppData/Roaming/...). Resolve one more level so you delete the right thing later:
[ -L ~/.agents/skills/$name ] && echo "agents entry ALSO a symlink -> $(readlink ~/.agents/skills/$name)"
```

Then read `~/.agents/.skill-lock.json`. Its shape is:

```jsonc
{ "version": 3,
  "skills": { "<name>": { "source": "mattpocock/skills", "sourceUrl": "https://…", … } },
  "dismissed": […], "lastSelectedAgents": {…} }
```

The per-skill data lives under **`skills.<name>`**, not at the top level. This `source` field is the
**authoritative source-of-truth** — match it to decide if the skill belongs to the source the user
wants gone.

**Manifest is not complete.** Only skills installed by a lock-aware installer appear under `skills`.
User-authored or otherwise-installed skills (on this machine: `arkts-syntax-assistant`,
`karpathy-guidelines`, `netease-uu-booster`, …) exist on disk but have **no manifest entry**. A
missing entry does not mean "safe to delete" — see 1.5.

### 1.5 The shared-name trap — verify the source, do not trust the name

A skill named `tdd` could come from `mattpocock/skills`, from the `superpowers` plugin, or be the
user's own. **Never delete based on the folder name alone.** Confirm the `source` field in
`.skill-lock.json`, or — for marketplace plugins — the marketplace name from step 1.2.

**If the skill has no `.skill-lock.json` entry at all** (see 1.4), you have *lost* the source-of-truth.
This is the highest-risk case, not the safest: an unlisted skill is most likely **the user's own** or
hand-installed, and deleting it is unrecoverable. Do **not** infer it belongs to the target just
because the name matches. Treat "no manifest entry" as an automatic trigger for 1.7 (stop and ask),
unless the user explicitly named that exact skill for removal.

If the target's source is still unclear after these checks, go to Phase 1.6.

### 1.6 Cross-check against the original GitHub repo (when source is ambiguous)

If the user gave a repo (e.g. `https://github.com/mattpocock/skills`) but you're not sure which
on-disk skills came from it, fetch the repo's `skills/` directory listing to enumerate every skill
that repo ships:

```
WebFetch https://github.com/<owner>/<repo>
  → "List every folder under the skills/ directory."
```

Compare that list against what's installed locally. Anything installed locally whose
`.skill-lock.json` `source` matches `<owner>/<repo>` is part of the target.

### 1.7 STOP and ask the user when ambiguous

If after 1.1–1.6 you still cannot tell whether a given on-disk skill belongs to the target source
or to the user, **stop and ask**. Concretely present what you found and let the user pick. Do not
guess. Today's real example: `obsidian-vault` came from `mattpocock/skills`, but the user actively
uses Obsidian — only by asking did we keep it while removing the other nine.

Use `AskUserQuestion` for keep/remove decisions, especially for skills the user might depend on
(note editors, note vaults, git helpers, etc.).

## Phase 2 — DELETE (only after Phase 1 is complete and unambiguous)

Delete in this exact order. The order matters: remove config first so nothing reloads the target,
then symlinks, then real folders, then manifest records.

### Model A (marketplace plugin) — 4 steps

1. **Config — `settings.json`**: delete the `extraKnownMarketplaces.<marketplace>` block (use Edit,
   keep valid JSON).
2. **Config — `settings.local.json`**: delete the `enabledPlugins."<plugin>@<marketplace>"` entry.
   If `enabledPlugins` becomes empty, leave it as `{}`.
3. **Cache**: `rm -rf ~/.claude/plugins/cache/<marketplace>`
4. **Marketplace source**: `rm -rf ~/.claude/plugins/marketplaces/<marketplace>`

### Model B (user-level skill) — for EACH target skill

1. **Visible entry** `~/.claude/skills/<name>`: `rm -rf` it. If it was a symlink (1.4), this removes
   only the link. If it was a real directory, this removes the skill itself — that's fine, but it
   means step 2 may find nothing.
2. **Real folder** `~/.agents/skills/<name>`: `rm -rf` it. But if 1.4 showed this entry is *itself*
   a symlink to somewhere else (e.g. `~/AppData/...`), deleting the link leaves the real payload
   behind — decide with the user whether that external target should also go (often it shouldn't;
   it may be a separate app's folder).
3. **Manifest record**: delete the **`skills.<name>`** key from `~/.agents/.skill-lock.json` — the
   entry is nested under the top-level `skills` object, *not* at the root. Never touch `version`,
   `dismissed`, or `lastSelectedAgents`. If the skill had no entry (1.4/1.5), skip this step.

For Model B, edit `.skill-lock.json` with a JSON-aware tool so structure stays valid — delete the
nested key, not the top level:

```bash
python -c "import json,sys; p=r'C:/Users/<user>/.agents/.skill-lock.json'; \
d=json.load(open(p,encoding='utf-8')); d['skills'].pop('<name>', None); \
json.dump(d, open(p,'w',encoding='utf-8'), indent=2, ensure_ascii=False)"
```

## Phase 3 — VERIFY

After deleting, confirm the target is gone AND that protected skills survived:

```bash
# target should be gone
[ -e ~/.claude/skills/<name> ] && echo "STILL EXISTS (bad)" || echo "removed (good)"
[ -e ~/.agents/skills/<name> ] && echo "STILL EXISTS (bad)" || echo "removed (good)"
# protected skills must still be there
ls -d ~/.agents/skills/<protected-skill>
```

For Model A, also re-list `plugins/cache/` and `plugins/marketplaces/` to confirm the marketplace
folder is gone from **both**, and grep settings to confirm the registration entry is gone. Note the
two folders are not always symmetric — a marketplace can be registered/cloned under
`marketplaces/` without a matching `cache/` entry (or vice versa). Check both independently; do not
assume clearing one clears the other.

## Phase 4 — REPORT

Tell the user, in plain language:
- What was removed (each skill/folder/config entry), grouped by storage model
- What was deliberately kept and why (e.g. "kept obsidian-vault because you use Obsidian")
- **Important — session cache caveat**: The deleted plugin/skill may still show up if you try to
  invoke it right now (e.g. `/help` still lists it, or the skill's trigger words still fire). This is
  because Claude Code loaded it into the **current session's memory** at startup. It is genuinely
  deleted from disk; the ghost appearance is only session cache. **Restart Claude Code** (fully
  quit and reopen) for removal to take full effect — after restart it will be completely gone.

## Hard rules

- **Investigate before deleting.** No `rm` in Phase 1.
- **Never `rm -rf ~/.agents/skills/` wholesale** — it's shared across sources.
- **Never delete by folder name alone** — confirm the `source` first.
- **No manifest entry ≠ safe to delete.** An unlisted skill is most likely the user's own — stop and ask.
- **Don't assume the visible skill is a symlink** — `test -L` first; it may be a real copied folder.
- **When unsure of the source, stop and ask the user.** Do not guess.
- **Edit JSON config carefully** — keep it valid; never break the rest of settings.json.
- **Windows note:** `~` resolves to `C:\Users\<user>`. Symlinks created by installers may be locked
  if Claude Code is running; if `rm` fails with a lock error, ask the user to fully quit Claude
  Code and retry. Never force-kill processes without asking.

## Quick reference — where things live

```
Marketplace plugin:
  ~/.claude/plugins/cache/<market>/
  ~/.claude/plugins/marketplaces/<market>/
  ~/.claude/settings.json            → extraKnownMarketplaces.<market>
  ~/.claude/settings.local.json      → enabledPlugins."<plugin>@<market>"

User-level skill (symlink model):
  ~/.claude/skills/<name>            → symlink (visible)
  ~/.agents/skills/<name>            → real folder
  ~/.agents/.skill-lock.json         → source-of-truth manifest (source / sourceUrl)
```
