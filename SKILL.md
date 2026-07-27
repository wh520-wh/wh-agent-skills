---
name: run-plan
description: Execute an existing implementation plan (markdown). Asks user to choose subagent mode (fresh subagent per task + review) or inline mode (single session). Model decides worktree need based on risk. Includes branch finishing and optional code review (user-consent only).
disable-model-invocation: true
---

# Run Plan

Execute an existing implementation plan (markdown file) end to end: load plan → set up workspace → execute tasks → review → finish branch → optional code review.

**Announce at start:** "I'm using the run-plan skill to execute this plan."

**Core principle:** One skill, two execution modes, full workflow. The user picks the mode; the model picks the workspace isolation. Never starts on main/master without explicit consent.

## Step 0: Choose Execution Mode

Ask the user (do not proceed until they pick):

```
How should I execute this plan?

1. Subagent mode — Dispatch a fresh implementer subagent per task, review after each, broad final review. Higher quality, isolated context per task, slower. Best for complex or risky plans.
2. Inline mode — Execute all tasks in this session, no subagents. Faster, simpler. Best for small or simple plans.

Which mode?
```

Honor the choice. Do not switch modes mid-execution without asking.

## Step 1: Load Plan and Set Up Workspace

### 1.1 Load and Critically Review the Plan

1. Read the plan file. If the user did not give a path, look under `docs/superpowers/plans/`, `docs/plans/`, or ask.
2. Review critically: identify questions, concerns, or conflicts between tasks or with the plan's Global Constraints.
3. **If concerns:** raise them with the user as one batched question before starting — each finding beside the plan text that triggers it, asking which governs.
4. **If clean:** proceed without comment.

Create a todo per task.

### 1.2 Workspace Isolation — Model Decides

**Judge whether this work needs an isolated worktree:**

- **Create a worktree** when the work is large or dangerous: multi-file changes, long-running, risky refactors, broad surface area, anything that could break the current branch.
- **Work in place** when the work is small or safe: single-file fixes, additive changes, quick tasks, docs.

This is your call. Weigh the plan's scope and risk. When unsure, lean toward a worktree for safety.

**If you decide to create a worktree:**

Detect existing isolation first — never create a nested worktree inside an existing one:

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
git rev-parse --show-superproject-working-tree 2>/dev/null  # submodule guard
```

- `GIT_DIR != GIT_COMMON` (and not a submodule): already in a linked worktree. Skip creation, use this workspace. Report: "Already in isolated workspace at `<path>` on branch `<name>`."
- `GIT_DIR == GIT_COMMON` (or in a submodule): normal repo. Prefer any native worktree tool your platform provides (`EnterWorktree`, `/worktree`, `--worktree`). Using `git worktree add` when a native tool exists creates phantom state the harness can't manage. Only fall back to git if no native tool exists.

Git fallback — directory priority: existing `.worktrees/` > existing `worktrees/` > `~/.config/superpowers/worktrees/<project>/` (legacy global) > default `.worktrees/` at project root. If both `.worktrees/` and `worktrees/` exist, `.worktrees/` wins.

```bash
# MUST verify project-local directory is gitignored before creating
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
# If NOT ignored: add to .gitignore and commit before proceeding.

project=$(basename "$(git rev-parse --show-toplevel)")
git worktree add ".worktrees/$BRANCH_NAME" -b "$BRANCH_NAME"
cd ".worktrees/$BRANCH_NAME"
```

**Sandbox fallback:** if `git worktree add` fails with a permission error, tell the user the sandbox blocked worktree creation and work in the current directory instead.

Then run project setup (auto-detect: `npm install` / `cargo build` / `pip install -r requirements.txt` or `poetry install` / `go mod download`) and verify a clean test baseline. If baseline tests fail, report failures and ask whether to proceed.

**If you decide to work in place:**

Verify a clean baseline:
```bash
npm test / cargo test / pytest / go test ./...
```
If tests fail, report and ask whether to proceed.

### 1.3 Ledger Setup (subagent mode only)

Conversation memory does not survive compaction. Controllers that lost their place have re-dispatched entire completed task sequences — the single most expensive failure observed. Track progress in a ledger file, not only in todos.

- Each plan owns a workspace: run `scripts/sdd-workspace PLAN_FILE` (from this skill's directory) — it prints the plan's git-ignored directory (`<repo-root>/.superpowers/sdd/<plan-basename>/`), home to every artifact for THIS plan: ledger, briefs, reports, review packages. Another plan's directory is never yours to read or write.
- Check for this plan's ledger at `<workspace>/progress.md`. If its first line names your plan file, tasks with a `Task <N>: complete` line are DONE — do not re-dispatch them; resume at the first task without one. A task whose last line is a fix round is mid-loop: resume the loop at the next round.
- Create the ledger with identity as the first line: `# SDD ledger - plan: <plan file path>`.
- The ledger is your recovery map: the commits it names exist in git even when your context no longer remembers creating them. After compaction, trust the ledger and `git log` over your own recollection.
- `git clean -fdx` will destroy the workspace (it's git-ignored scratch); if that happens, recover from `git log`.

## Step 2: Execute Tasks

### 2A. Subagent Mode

#### Model Selection

Use the least powerful model that can handle each role to conserve cost and increase speed. **Always specify the model explicitly when dispatching a subagent** — an omitted model inherits your session's model (often the most capable and most expensive), silently defeating this section.

- **Mechanical implementation tasks** (isolated functions, clear specs, 1-2 files): fast, cheap model. Most implementation tasks are mechanical when the plan is well-specified.
- **Integration and judgment tasks** (multi-file coordination, pattern matching, debugging): standard model.
- **Architecture and design tasks**: most capable available model. The final whole-branch review is one of these — dispatch it on the most capable available model, not the session default.
- **Review tasks**: choose a model scaled to the diff's size, complexity, and risk. A small mechanical diff does not need the most capable model; a subtle concurrency change does.
- **Fix-loop escalation (rounds 4-5)**: use a model at least one tier above the implementer that got stuck.

**Turn count beats token price.** The cheapest models routinely take 2-3× the turns on multi-step work — costing more overall. Use a mid-tier model as the floor for reviewers and for implementers working from prose descriptions. When the task's plan text contains the complete code to write, the implementation is transcription plus testing: use the cheapest tier.

#### The Task Loop

Everything you paste into a dispatch prompt — and everything a subagent prints back — stays resident in your context for the rest of the session. Hand artifacts over as files.

##### 1. Dispatch the implementer

Record BASE (`git rev-parse HEAD`) before dispatching — the review package and fix-round diffs need it.

- **Task brief:** before dispatching, run `scripts/task-brief PLAN_FILE N` — it extracts the task's full text to a uniquely named file and prints the path. Compose the dispatch so the brief stays the single source of requirements. Your dispatch should contain: (1) one line on where this task fits in the project; (2) the brief path, introduced as "read this first — it is your requirements, with the exact values to use verbatim"; (3) interfaces and decisions from earlier tasks that the brief cannot know; (4) your resolution of any ambiguity you noticed in the brief; (5) the report-file path and report contract. Exact values appear only in the brief. Never make a subagent read the whole plan file.
- **Report file:** name the implementer's report file after the brief (brief `…/task-N-brief.md` → report `…/task-N-report.md`). The implementer writes the full report there and returns only status, commits, a one-line test summary, and concerns.
- A dispatch prompt describes one task, not the session's history. Do not paste accumulated prior-task summaries into later dispatches.
- Record the implementer's agent identity from the dispatch result — fix-loop rounds 1-3 resume this agent.
- Never dispatch multiple implementation subagents in parallel (conflicts).

Template: [implementer-prompt.md](implementer-prompt.md)

##### 2. Handle the report

Implementer subagents report one of four statuses:

- **DONE:** Generate the review package (`scripts/review-package PLAN_FILE BASE HEAD`, from this skill's directory — it prints the unique file path it wrote; BASE is the commit you recorded before dispatching, never `HEAD~1` which silently drops all but the last commit of a multi-commit task), then dispatch the task reviewer with the printed path.
- **DONE_WITH_CONCERNS:** Read the concerns before proceeding. If about correctness or scope, address before review. If observations, note and proceed to review.
- **NEEDS_CONTEXT:** Provide the missing context and re-dispatch.
- **BLOCKED:** Assess the blocker: (1) context problem → provide more context, re-dispatch same model; (2) needs more reasoning → re-dispatch on a more capable model; (3) task too large → break into smaller pieces; (4) plan itself wrong → escalate to the human.

**Never** ignore an escalation or force the same model to retry without changes.

If the implementer asks questions — before starting or mid-task — answer clearly and completely, don't rush it into implementation.

##### 3. Review the task

Per-task reviews are task-scoped gates. The broad review happens once, at the final whole-branch review. Never skip the task review. Implementer self-review never replaces it; both are needed.

- Hand the reviewer its diff as a file: run `scripts/review-package PLAN_FILE BASE HEAD` and pass the reviewer the file path it prints. The output never enters your own context, and the reviewer sees the commit list, stat summary, and full diff in one Read call. Use the BASE you recorded before dispatching — never `HEAD~1`. Never dispatch a task reviewer without a diff file.
- **Reviewer inputs:** the task reviewer gets three paths — the same brief file, the report file, and the review package — plus the global constraints that bind the task.
- The global-constraints block is the reviewer's attention lens. Copy binding requirements verbatim from the plan's Global Constraints: exact values, exact formats, stated relationships. The reviewer's template already carries process rules (YAGNI, test hygiene) — the constraints block is for what THIS project's spec demands.
- Do not add open-ended directives ("check all uses") without a concrete, task-specific reason.
- Do not pre-judge findings — never instruct a reviewer to ignore or not flag a specific issue. If you believe a finding would be a false positive, let the reviewer raise it and adjudicate in the review loop.
- The task reviewer may report "⚠️ Cannot verify from diff" items — requirements in unchanged code or spanning tasks. These do not block the review, but you must resolve each yourself before marking the task complete. If you confirm a real gap, treat it as a failed spec review — it enters the fix loop.

Template: [task-reviewer-prompt.md](task-reviewer-prompt.md)

##### 4. The fix loop

The loop triggers when the review reports spec ❌, any Critical or Important finding, or a ⚠️ item you confirmed as a real gap.

Two routes leave the loop immediately:

- **Minor findings:** record in the progress ledger as you go (`Task <N>: minor (deferred): <one-liner>`), point the final review at that list. Minor findings never enter the loop.
- **Plan-mandated findings:** a finding that conflicts with what the plan's text requires is the human's decision — present the finding and the plan text, ask which governs. Do not dismiss, do not dispatch a fix contradicting the plan without asking.

Everything else enters the loop. A fix round is one fix dispatch plus one scoped re-review. **Five rounds maximum per task:**

- **Rounds 1-3 — resume the original implementer.** Send it the open findings verbatim. Its context is intact. If your harness cannot send another message to a live subagent, dispatch a fresh implementer carrying the brief path, the report-file path, and the findings.
- **Rounds 4-5 — dispatch a fresh implementer on a more capable model**, with the brief path, report-file path, open findings, and framing: "A prior implementer attempted this task [N] times; you own it now. Read the report file for what was tried."

**Every round:** the implementer fixes, re-runs covering tests, appends its fix report to the same report file, returns the short contract. Before re-dispatching the reviewer, confirm the fix report contains the covering tests, the command run, and the output. Name the covering test files in the fix message.

**The re-review is scoped.** Run `scripts/review-package PLAN_FILE FIX_BASE HEAD` where FIX_BASE is the head the previous review saw, and dispatch [re-review-prompt.md](re-review-prompt.md) with the findings list, brief, report file, and printed diff path. The re-reviewer verdicts each finding ADDRESSED or NOT ADDRESSED and flags new breakage in the fix diff only. New Critical/Important breakage joins the open findings list. Out-of-scope observations go to the ledger as deferred minors.

**After each round,** append to the ledger: `Task <N>: fix round <R>/5 (<X> addressed, <Y> open - <finding one-liners>; commits <a7>..<b7>)`

Never fix findings yourself in the controller session — your context stays clean for coordination, and controller fixes skip review.

**The breaker.** When round 5's re-review still leaves findings open, stop dispatching. Adjudicate each open finding yourself — you hold the plan and cross-task context the reviewer lacks:

- **Reviewer wrong, or contestable:** park it — `Task <N>: parked - <finding> - ruling: <why the code stands>`. The final review sees both sides.
- **Real, but nothing downstream builds on it:** park it the same way, ruling says it's real and deferred.
- **Real and load-bearing** — a later task builds on it, or it reveals a plan defect: STOP. Append `Task <N>: BLOCKED - <reason>` and report to the user with the finding, the plan text it collides with, and the fix history.

Adjudicate only at the cap. Adjudicating earlier to end a loop is pre-judging. Every adjudication is a ledger entry — a silent discard is forbidden.

##### 5. Complete the task

When the review comes back clean — or every open finding is parked with a ruling at the cap — append the completion line to the ledger in the same message as your other bookkeeping:

- `Task <N>: complete (commits <base7>..<head7>, review clean)`
- `Task <N>: complete (commits <base7>..<head7>, <K> parked)` after a tripped breaker

Then mark the todo complete and move on. Never move to the next task while the review has open Critical/Important issues that are neither fixed nor parked-with-ruling at the cap.

**Continuous execution:** Do not pause to check in with the user between tasks. Execute all tasks from the plan without stopping. The only reasons to stop are: BLOCKED status you cannot resolve, ambiguity that genuinely prevents progress, or all tasks complete. "Should I continue?" prompts waste time — the user asked you to execute the plan, so execute it.

### 2B. Inline Mode

Load plan, review critically, execute all tasks, report when complete. No subagents — you execute every step yourself in this session.

For each task:
1. Mark as in_progress
2. Follow each step exactly (the plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

**When to stop and ask:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

Ask for clarification rather than guessing. Don't force through blockers — stop and ask.

**Return to the critical review (1.1) when:**
- The user updates the plan based on your feedback
- The fundamental approach needs rethinking

## Step 3: Final Whole-Branch Review (subagent mode only)

The final whole-branch review gets a package too: run `scripts/review-package PLAN_FILE MERGE_BASE HEAD` (MERGE_BASE = the commit the branch started from, e.g. `git merge-base main HEAD`) and include the printed path in the final review dispatch, so the final reviewer reads one file instead of re-deriving the branch diff. Dispatch on the most capable available model, using [code-reviewer.md](code-reviewer.md). Point it at the ledger's deferred-minor and parked lines so it can triage which must be fixed before merge.

If the final whole-branch review returns findings, dispatch ONE fix subagent with the complete findings list — not one fixer per finding. Per-finding fixers each rebuild context and re-run suites; a real session's final-review fix wave cost more than all its tasks combined. Then run exactly one scoped re-review of the fix wave (`scripts/review-package PLAN_FILE FIX_BASE HEAD` over the fix range, [re-review-prompt.md](re-review-prompt.md)). Adjudicate any residual findings as in the task loop's breaker: park with rulings, or stop on load-bearing ones. There is no second fix wave.

## Step 4: Finish the Development Branch

Both modes converge here. Verify tests, present structured options, execute the user's choice, clean up.

### 4.1 Verify Tests

Before presenting options, verify tests pass:
```bash
npm test / cargo test / pytest / go test ./...
```
If tests fail: stop. Do not proceed to options until tests pass.

### 4.2 Detect Environment

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
```

| State | Menu | Cleanup |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON` (normal repo) | Standard 4 options | No worktree to clean up |
| `GIT_DIR != GIT_COMMON`, named branch | Standard 4 options | Provenance-based (see 4.6) |
| `GIT_DIR != GIT_COMMON`, detached HEAD | Reduced 3 options (no merge) | No cleanup (externally managed) |

### 4.3 Determine Base Branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```
Or ask: "This branch split from main — is that correct?"

### 4.4 Present Options

**Normal repo and named-branch worktree — present exactly these 4:**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**Detached HEAD — present exactly these 3:**

```
Implementation complete. You're on a detached HEAD (externally managed workspace).

1. Push as new branch and create a Pull Request
2. Keep as-is (I'll handle it later)
3. Discard this work

Which option?
```

Don't add explanation — keep options concise.

### 4.5 Execute Choice

**Option 1 — Merge Locally:**
```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
git checkout <base-branch>
git pull
git merge <feature-branch>
<test command>  # verify tests on merged result
```
Only after merge succeeds: cleanup worktree (4.6), then `git branch -d <feature-branch>`.

**Option 2 — Push and Create PR:**
```bash
git push -u origin <feature-branch>
gh pr create --title "<title>" --body "## Summary
<2-3 bullets>

## Test Plan
- [ ] <verification steps>"
```
Do NOT clean up worktree — user needs it alive to iterate on PR feedback.

**Option 3 — Keep As-Is:**
Report: "Keeping branch <name>. Worktree preserved at <path>." Don't cleanup worktree.

**Option 4 — Discard:**
Confirm first:
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```
Wait for exact "discard" confirmation. If confirmed: cleanup worktree (4.6), then `git branch -D <feature-branch>`.

### 4.6 Cleanup Workspace (Options 1 and 4 only)

Options 2 and 3 always preserve the worktree.

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

- **If `GIT_DIR == GIT_COMMON`:** normal repo, no worktree to clean up. Done.
- **If worktree path is under `.worktrees/`, `worktrees/`, or `~/.config/superpowers/worktrees/`:** this skill created it — we own cleanup:
  ```bash
  MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
  cd "$MAIN_ROOT"
  git worktree remove "$WORKTREE_PATH"
  git worktree prune  # self-healing: clean up stale registrations
  ```
- **Otherwise:** the host environment owns this workspace. Do NOT remove it. Leave it in place.

## Step 5: Code Review (Ask User First)

After finishing, ask the user:

```
Plan execution complete. Would you like me to run a final code review?

1. Yes — dispatch a code reviewer subagent
2. No — we're done
```

**Only if the user explicitly agrees ("Yes")** — never run code review without consent.

1. Get git SHAs:
   ```bash
   BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main, or the merge-base
   HEAD_SHA=$(git rev-parse HEAD)
   ```

2. Dispatch a code reviewer subagent using the Task tool with `general-purpose` type, filling the template at [code-reviewer.md](code-reviewer.md). The reviewer gets precisely crafted context — never your session's history. Placeholders:
   - `{DESCRIPTION}` — Brief summary of what you built
   - `{PLAN_OR_REQUIREMENTS}` — What it should do
   - `{BASE_SHA}` — Starting commit
   - `{HEAD_SHA}` — Ending commit

3. Act on feedback:
   - Fix Critical issues immediately
   - Fix Important issues before proceeding
   - Note Minor issues for later
   - Push back if the reviewer is wrong (with technical reasoning, show code/tests that prove it)

## Red Flags

**Never:**
- Start implementation on main/master without the user's explicit consent
- Skip the Step 0 mode-choice question
- Force through blockers — stop and ask
- Proceed with failing tests
- Skip the task review in subagent mode (implementer self-review never replaces it)
- Fix findings yourself in the controller session — resume the implementer
- Silent-discard a finding — every adjudication is a ledger entry
- Run code review without explicit user consent
- Delete work without typed "discard" confirmation
- Force-push without explicit request
- Remove a worktree before confirming merge success
- Clean up worktrees you didn't create (provenance check)
- Run `git worktree remove` from inside the worktree

**Always:**
- Ask the user to pick mode before executing
- Review the plan critically before starting
- Judge worktree need by the plan's scope and risk
- Track progress in a ledger (subagent mode) — it survives compaction
- Specify the model explicitly when dispatching subagents
- Verify tests before offering finish options
- Present exactly 4 (or 3 for detached HEAD) structured options at finish
- Ask before running code review
