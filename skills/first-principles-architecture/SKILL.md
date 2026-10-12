---
name: first-principles-architecture
description: Apply first-principles architectural reasoning to technical plans, system designs, refactoring proposals, codebase problems, and major changes. Use only when the user explicitly invokes this skill by name or with $first-principles-architecture; never activate it automatically from topic similarity.
disable-model-invocation: true
version: 2
---

# First-Principles Architecture

Use this skill only after explicit user invocation. Treat it as a thinking lens, not a mandatory implementation ceremony, a report template, or a fixed workflow. Once invoked, keep using it for the duration of the current plan, feature, or refactoring task; step back when the topic changes, the approach is finalized, or the user asks to stop.

Orient automatically to what is being examined, and do not ask the user to clarify it when the context already makes it clear:

- An unexecuted plan: scrutinize the plan rather than executing it—judge whether it patches old structure or builds the right target structure.
- A new feature: judge where it should land in the project's core and what old-structure problems it exposes.
- An existing codebase: find the root problem yourself from code, directories, tests, data flow, and call graphs.
- Code being changed: judge whether the current edit fixes the system model or keeps patching the old one.

A directory tree shows how the system grew, not what it is: when surveying unfamiliar code, read the entry points, the data model, and the tests first-they expose the real architecture and its invariants fastest.

Reconstruct the right system from its purpose before reasoning from the current code. Do not assume that first-principles thinking requires a rewrite.

## Establish the target

Start with the outcome the system must produce for users and operators. Identify the smallest set of essential domain concepts, invariants, responsibilities, state owners, execution rules, and external interfaces required to produce that outcome.

Temporarily ignore existing file names, classes, compatibility layers, and historical module boundaries while deriving this target model. Treat business rules, data compatibility, operational constraints, and verified user behavior as real constraints. Treat the current arrangement of code as evidence, not as a requirement.

Ask:

- What must remain true regardless of implementation?
- What would the system look like if designed today with all current knowledge?
- Which concept owns each important decision and piece of state?
- Where should complexity live so callers face a small, coherent interface?
- Which distinctions are essential, and which exist only because the system evolved through patches?

## Compare target and history

Inspect the current system only after forming a provisional target model. Separate what exists into four categories: preserve, reshape, replace, and delete.

Preserve stable domain capabilities whose behavior and ownership already fit the target model. Reshape code when the underlying concept is correct but its interface or placement is weak. Replace a bounded subsystem when its central model, control flow, or state ownership conflicts with the target. Delete compatibility layers, duplicate paths, and obsolete concepts after cutover.

Do not reward reuse for its own sake. Reuse behavior and knowledge that still belong in the target architecture; do not preserve accidental structure merely because it already exists.

A verdict about unnamed code is a hypothesis, not a finding: attach every classification to specific files, modules, or interfaces, and when you have sampled the codebase rather than read it whole, say what was read and what was not.

Nothing is dead until proven dead everywhere: a symbol absent from the directories you read may still live in tests, config, or dynamic dispatch.

## Choose the change strategy

Before selecting a strategy, align with the user on how aggressive the change may be when they have not said so, and recommend a level:

- **Conservative**: remove dead code and local mess only; avoid touching public interfaces.
- **Moderate (default)**: adjust module boundaries, merge duplicated logic, replace local old abstractions.
- **Destructive-creative**: delete old models, cut old paths, rebuild core structure—but only with evidence, a migration plan, and verification, never as a blind rewrite.

Under the destructive level, default toward deleting the old: keep a piece of legacy only when it can be shown to still carry real business behavior, data compatibility, failure handling, or user expectations; otherwise list it as a deletion, merge, or replacement candidate. Even under the destructive level, avoid extreme rewrites—explain rationale and risk and get confirmation before large deletions, public-interface breaks, data migrations, or core-path replacements.

Then choose among these strategies from evidence:

- Use local refactoring when the core model is sound and the problem is limited to implementation quality.
- Use incremental architectural migration when old and new behavior must coexist for a genuine operational reason.
- Use bounded clean replacement when one subsystem has a fractured model but surrounding domain capabilities remain sound.
- Recommend a full rewrite only when defects are systemic, boundaries cannot isolate them, and preserving the implementation costs more than reconstructing verified behavior.

When evidence does not separate two strategies, prefer the one that degrades gracefully: every intermediate state shippable, every completed step valuable even if the effort stops midway.

Prefer the smallest change that makes the architecture conceptually complete. Do not prefer the smallest diff when it leaves contradictory models or permanent migration machinery behind.

## Protect conceptual integrity

Evaluate whether the proposal reads as one coherent system:

- Use one domain language for the same concepts.
- Give every mutable state a clear source of truth.
- Give every user action one authoritative execution path.
- Keep public interfaces few and meaningful; keep implementation details private.
- Avoid parallel runtimes, duplicate writes, speculative abstractions, pass-through modules, and permanent compatibility seams.
- Make transitional code temporary, explicitly removable, and tied to a cutover condition that can actually be checked-a metric, a date, or a flag flip, never "when things stabilize".
- Verify the final architecture through its production-facing interfaces, and prove obsolete paths gone rather than assume it: search the repository for old entry points and references, run the tests through the new path, and check logs or telemetry for remaining traffic to what was cut.

When reviewing a plan, ensure its task order constructs the target architecture rather than repeatedly modifying code that a later task deletes. Require the plan to state what is created, preserved, extracted, migrated, cut over, and removed. Make the final state understandable without knowing the migration history.

## Communicate the reasoning

State the root structural problem before proposing modules or files. Distinguish observations from assumptions, and mark unresolved uncertainties as assumptions rather than interrogating the user. Batch related questions into one round, at most two, each with a recommended answer; prefer answers you can get yourself from code, tests, or commit history. Do not default to an architecture report-fold the verdict into the current discussion. When the user's chosen direction conflicts with the target model, state the conflict and its consequence once, clearly, then execute their decision: the trade-off is theirs to own. Do not change code, files, or plans unless the user asks for changes.

## Avoid false first principles

Do not use "first principles" as decoration for a preferred solution. Do not infer that old code is wrong because it is old, or that a clean-slate design is correct because it looks simpler on paper. Account for behavior encoded in tests, data formats, operations, failure handling, and user expectations.

Reject solutions that achieve visual neatness by moving complexity elsewhere, hiding migration risk, or discarding validated domain knowledge. The objective is conceptual integrity and lower long-term complexity, not novelty.
