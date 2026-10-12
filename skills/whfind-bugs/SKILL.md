---
name: whfind-bugs
description: Use when finding bugs, defects, or architectural weaknesses in a codebase, or auditing code quality and correctness before reporting issues.
license: MIT
---

# Find Bugs

## Overview

Hunt bugs by **proposing candidates then adversarially killing the wrong ones**. A bug is not "found" until a fresh skeptic subagent tried to refute it and failed. Expect to reject ~half your candidates — a hunt that confirms everything has no filter, and plausible-but-wrong bugs survive.

**Core principle:** Broad proposal + ruthless adversarial filtering. Never report a bug you haven't tried to disprove.

## When to Use

- Asked to "find bugs / defects / weaknesses / issues" in a codebase
- Auditing code quality, correctness, or security
- Reviewing before reporting or fixing

Not for: a single known bug you're already debugging (use systematic-debugging).

## The Loop

```
PROPOSE candidate (4 elements)
  → ADVERSARIALLY VERIFY via fresh skeptic subagent
    → skeptic refutes / downgrades? REJECT, log reason, continue
    → survives? main loop must agree-at-a-glance
      → can't instantly endorse? still unconfirmed, keep digging or drop
```

**Every candidate gets the four elements before verification:**
1. **Location** — file + line(s)
2. **Phenomenon** — what the code actually does (quote it)
3. **Impact** — user-visible consequence
4. **Evidence** — the specific code path proving it

## The Skeptic Subagent (mandatory, no shortcuts)

Dispatch a **fresh** subagent (no shared context, not you) instructed to **refute** the candidate. "Fresh" means it has not seen your reasoning — it re-reads the cited code from scratch.

### How to dispatch a fresh skeptic — by runtime

This skill is runtime-neutral. Use your runtime's "delegate to an isolated agent" mechanism:

| Runtime | Mechanism |
|---|---|
| Claude Code | `Task` tool / subagent (pass the full candidate, no prior context) |
| Codex CLI | spawn a fresh agent turn with only the candidate as input |
| OpenCode / OpenClaw / Hermes | your runtime's sub-agent / delegate call |
| No sub-agent available? | open a clean context yourself, paste ONLY the candidate + the five questions below, and answer them as if you'd never seen the proposal. Re-reading your own reasoning is NOT a substitute. |

### Skeptic dispatch prompt (copy verbatim)

> You are a fresh skeptic who has not seen any prior analysis. Your ONLY job is to REFUTE this bug candidate. Default to "it's not a real/major bug" unless the code forces you otherwise. Independently read the cited lines yourself — do not trust the description.
>
> Candidate:
> - Location: <file + lines>
> - Phenomenon: <what the code does>
> - Claimed impact: <consequence>
> - Evidence: <code path>
>
> Do the three steps below in order. Skip or hand-wave any → your answer is invalid.
>
> STEP 1 — Restate (proves you read the candidate): in your own words, 1-2 sentences on what the bug is. Do NOT copy the candidate's wording.
>
> STEP 2 — Answer each of the five questions with CHECKABLE evidence (this is where independent code-reading is proven). Bare assertion (no quote AND no search-scope stated) = that question is invalid.
>
>   - For questions with a single-line answer: quote the line you read + line number.
>   - For absence / search / cross-file answers: state the scope you searched + what you found or did not find.
>
>   1. **Code facts** — did the proposer misread? (e.g. "overwrite" vs "merge", "never passed" vs "passed with default")
>   2. **Design boundary** — is there an explicit "by design" signal? Search comments, docstrings, sibling paths that DO the safe version. If the team clearly knows how to do X and does it elsewhere, that's evidence of a boundary, not a bug.
>   3. **Independent or derived?** — reachable on its own, or only as a consequence of another bug? A bug needing "zero auth + attacker changes config" is a footnote on the auth bug.
>   4. **Deployment reality** — does default config make this dormant? Feature/dependency on by default? Single-process or multi-worker? Existing locks serialize the path? Test covering it? Dormant-by-default ≠ major.
>   5. **Severity honesty** — even if real: data loss / hard failure / core-feature-broken = major; theoretical / low-probability / cosmetic = downgrade.
>
> STEP 3 — Verdict (must point to a specific STEP 2 question + its evidence; can't = invalid): confirmed / rejected / downgraded.
>
> Non-compliant answer (no restatement / bare-assertion evidence / verdict points to nothing) = you did not do your job; the answer is invalid. The main agent MUST re-dispatch a skeptic for any invalid answer and may NOT silently keep a candidate on an invalid verdict.

A candidate the skeptic confirms but you can't endorse at a glance is **still unconfirmed** — dig more or drop it.

## Why two layers

The skeptic filters *plausible-but-wrong*. Your at-a-glance gate filters *over-cautious-skeptic-kept-something-marginal*. Either alone leaks: self-review accepts your own bad ideas; a skeptic you defer to blindly lets weak survivors through. Both must pass.

## Quick Reference

| Step | Do | Don't |
|------|----|----|
| Propose | Cast wide, many candidates | Pre-filter for "obvious" ones |
| Verify | Fresh skeptic, instructed to refute | Self-verify by re-reading |
| Gate | Endorse at a glance or drop | Defer to skeptic blindly |
| Reject | Log the reason, move on | Silently abandon |
| Report | Only confirmed survivors | Everything you proposed |

## Common Mistakes (baseline failures this skill kills)

| Excuse / Behavior | Reality |
|---|---|
| "I read the code, it's confirmed" | Self-review shares your blind spot. Fresh skeptic or it's unverified. |
| Reports 100% of own findings | No filter = plausible-but-wrong survive. Reject ~half. |
| Flags a concurrency bug as major | Check default config + locks first. Dormant ≠ major. |
| Reports an auth-dependent issue as independent | If it needs another bug to trigger, it's a footnote. |
| "No comment says it's by design" | Absence of a boundary ≠ presence of a bug. Check sibling paths that *do* the thing. |
| Skeptic confirmed, so ship it | You must also endorse at a glance. Two layers, both required. |
| Treats first plausible framing as the bug | Skeptics often correct the *mechanism* (e.g. "tail-failure draft is full text, not garbage") — update the finding or drop it. |

## Red Flags — STOP

- About to report a bug no skeptic has tried to refute
- A hunt with zero rejections
- Calling a default-off / single-worker / lock-serialized path "major"
- Flagging something without checking whether the codebase does the safe version elsewhere (design-boundary check)
- "The skeptic might be wrong, I'll just report it anyway"

**All mean: run the skeptic, or drop the candidate.**

## Recording

Keep a running log in a file (e.g. `find-bugs-report.md`) or your session record:
- **Confirmed** (survived skeptic + at-a-glance): four elements + skeptic verdict
- **Rejected**: one-line reason each (wrong mechanism / derived / dormant / design-boundary)

Rejected candidates are evidence the filter worked — record them, don't hide them.
