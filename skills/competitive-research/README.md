# Competitive Research

> Stop collecting competitor tabs that cannot survive a product decision.

**Competitive Research turns primary-source evidence into a cited comparison matrix, an evidence ledger, and a roadmap with measurable acceptance signals.**

## What It Delivers

1. A dated Markdown decision report with direct, adjacent, potential, and baseline competitors.
2. A JSON evidence ledger that separates facts from inferences.
3. P0, P1, and P2 recommendations that cite evidence and define an acceptance signal.
4. A zero-dependency validator that catches missing sources, broken evidence references, absent priority tiers, and unsupported recommendations.

## Quick Start

Copy this prompt into any Agent Skills-compatible runtime:

```text
Use $competitive-research to compare competitors for this project, decide our strongest wedge, and write the report plus evidence ledger under docs/research/.
```

Validate the resulting artifacts:

```bash
python scripts/check_competitive_report.py docs/research/REPORT.md docs/research/LEDGER.json
```

## When To Use It

- "Find competitors and explain our real advantage."
- "Compare these products before we choose a roadmap."
- "Benchmark this feature against direct and adjacent alternatives."
- "Research the market, but show evidence for every important claim."
- "Decide whether this product wedge is actually differentiated."

## Evidence Contract

Use official product pages, docs, source code, pricing, releases, and owned papers for product facts. Search snippets, social posts, and third-party reviews are discovery clues, never feature evidence. Record inaccessible or stale sources as limitations rather than filling gaps with guesses.

See [the ledger schema](references/evidence-ledger-schema.md) and [the complete example](examples/minimal-report.md).

## Verify The Package

```bash
python -m unittest tests/test_validator.py
```

The test suite proves that the included real-source example passes and that a ledger with weak evidence, missing metadata, and unsupported recommendations fails.

## Safety Boundaries

- Does not claim desk research is an installation, benchmark, security review, or production test.
- Does not use search-result snippets or social posts as product facts.
- Does not fabricate competitors to meet a target count.
- Stops and records the gap when a material source is inaccessible or evidence is insufficient.

## Files

```text
competitive-research/
  SKILL.md                              Agent workflow and output contract
  README.md                             Installation and verification entry point
  LICENSE                               MIT license
  references/evidence-ledger-schema.md  Ledger fields and rules
  scripts/check_competitive_report.py   Zero-dependency static validator
  examples/                             Passing report and ledger
  tests/                                Validator tests and failing fixtures
  test-prompts.md                       Regression prompts and pass conditions
```
