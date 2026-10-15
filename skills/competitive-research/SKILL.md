---
name: competitive-research
description: Research a project's direct, adjacent, and potential competitors across GitHub, official product sites, documentation, pricing, releases, papers, and other primary sources; then produce an evidence-linked comparison, differentiated positioning, and prioritized product roadmap. Use when the user asks to find competitors, conduct market or competitive analysis, compare products or features, identify a product's core advantage, choose a product direction, or derive strategy from external evidence.
---

# Competitive Research

Turn cross-source competitor evidence into a decision, not a feature inventory. Deliver a cited report and a machine-checkable evidence ledger.

## Deliverables

For every research task, create these two dated files in the repository's established research/docs location. If none exists, use `docs/research/`.

- `YYYY-MM-DD-competitive-research.md`: the decision-ready report.
- `YYYY-MM-DD-competitive-research-ledger.json`: the evidence and recommendation ledger.

Read `references/evidence-ledger-schema.md` before creating the ledger. Run `python scripts/check_competitive_report.py <report.md> <ledger.json>` before reporting success.

## 1. Choose the smallest research mode

State the mode and decision in the report. Do not ask a question unless an answer would materially change the decision or target market.

| Mode | Use for | Minimum evidence |
| --- | --- | --- |
| Rapid | One feature, one market, or a short product decision | 3 competitors, 1 primary source each |
| Standard | Positioning or roadmap choice | 6 competitors across direct and adjacent groups, 1 primary source each |
| Deep | High-cost, irreversible, or go-to-market decision | 12 competitors including a potential-competitor watchlist, 2 sources for critical claims |

Classify every candidate as `direct`, `adjacent`, `potential`, or `baseline`. A baseline is an incumbent or non-AI alternative that defines the expected experience. Do not use a large competitor count to pad a weak decision.

## 2. Establish the local baseline

Inspect the product README, user guide, architecture notes, release notes, and observable behavior. Separate:

- shipped capabilities;
- planned work;
- user claims or assumptions;
- constraints such as privacy, deployment, model providers, budget, and target region.

Record the source of each local claim in the ledger. Do not compare a competitor's shipped feature against an unshipped local plan without labeling the difference.

## 3. Gather evidence, not snippets

Use multiple search vocabularies: category, desired outcome, workflow, architecture, and adjacent substitute. Prefer sources in this order:

| Grade | Source | Permitted use |
| --- | --- | --- |
| A | Official product site, docs, source code, pricing, release notes, owned paper | Supports factual product claims |
| B | Official presentation, public interview, marketplace listing, package registry | Supports bounded context; flag as self-described when relevant |
| C | Search snippets, social posts, third-party reviews, unauthenticated summaries | Discovery only; never supports a capability, pricing, security, or adoption claim |

For each material claim, create an evidence entry with a stable ID, exact source URL, source type, access date, locator, classification, and confidence. Use `fact` only for what the source directly states or demonstrates. Use `inference` for your interpretation and explain it in the claim.

## 4. Handle missing evidence honestly

- 404, login wall, rate limit, or inaccessible page: record the failed source in the report limits; seek one alternative A/B source; otherwise mark the claim `unverified` and exclude it from the comparison.
- Only C-grade evidence: use it to find a primary source, not as a citation.
- Stale pricing, releases, or activity: record the observed date and do not describe it as current.
- Too few credible competitors: report the actual count and explain the search boundary. Do not add distant products simply to satisfy a number.
- Network/tool failure: preserve the evidence collected, state the gap, and finish the bounded report. Never hang waiting for an unavailable search path.

## 5. Synthesize the decision

Compare only dimensions that matter to the decision. A useful default is:

1. User and job to be done
2. Workflow and user control
3. Information model, data ownership, and provenance
4. Reliability, review, recovery, and failure handling
5. UX/workbench, interoperability, and ecosystem
6. Cost, privacy, deployment, and operational burden

Identify table stakes, recognizable differentiators, adoption-blocking gaps, and explicit non-goals. Add a differentiation pressure test: explain why the proposed wedge is observable to the target user and why a stronger competitor has not already made it undifferentiated.

Do not recommend feature parity by default. Every P0/P1/P2 recommendation must reference one or more evidence IDs and include a measurable acceptance signal.

## 6. Write the report and ledger

Use this report outline exactly:

```markdown
# Competitive Research: <product/category>

- Date, mode, and decision
- Scope and evidence limits

## Executive Conclusion
<positioning, strongest threats, and wedge with [E#] citations>

## Current Product Baseline
<shipped facts and assumptions with [E#] citations>

## Competitor Comparison
| Competitor | Category | Evidence | Lesson | Do Not Copy |

## Cross-Market Patterns
<table stakes, differentiators, gaps, and non-goals with citations>

## Prioritized Roadmap
### P0
<recommendation, [E#] citations, acceptance signal>
### P1
...
### P2
...

## Research Limits and Next Validation
```

Keep source links and source metadata in the ledger. Cite their IDs in the report as `[E1]`, `[E2]`, and so on. Do not paste a raw search diary into the report.

## 7. Verify and hand off

Run the validator. It rejects malformed ledgers, missing primary-source fields, unknown report citations, unsupported recommendation evidence, missing priority tiers, and missing acceptance signals.

Then verify manually:

- every comparison row has a cited, relevant source;
- facts, inferences, and recommendations are visibly separate;
- the report includes at least one non-goal;
- each priority tier can be traced to evidence and has an acceptance signal;
- all failed or unverified research paths appear in the limits section.

For high-stakes decisions, recommend a separate hands-on validation of the top two or three alternatives. Do not describe desk research as an installation, benchmark, security review, or production test.
