# Competitive Research: Local-first knowledge management

- Date: 2026-07-21
- Mode: Rapid
- Decision: Decide whether local Markdown ownership is a credible wedge.
- Scope: Official product and documentation pages only.

## Executive Conclusion

Local file ownership is a recognizable wedge when it is paired with reliable search and backup rather than presented as a privacy slogan. Obsidian documents that it stores notes as local Markdown files, while Notion positions itself as a connected workspace. [E1] [E2]

## Current Product Baseline

The hypothetical product is local-first and has no collaboration feature. This is a user assumption, not a shipped-product fact.

## Competitor Comparison

| Competitor | Category | Evidence | Lesson | Do Not Copy |
| --- | --- | --- | --- | --- |
| Obsidian | Direct | [E1] | Make ownership concrete through plain files. | Do not assume a file format alone creates a differentiated workflow. |
| Notion | Adjacent | [E2] | Connected workspaces set collaboration expectations. | Do not add cloud collaboration before the local workflow is reliable. |

## Cross-Market Patterns

Table stakes are search and durable storage. The differentiator is inspectable local ownership. A non-goal is real-time multi-user collaboration in the first release. [E1] [E2]

## Prioritized Roadmap

### P0

Ship Markdown import, export, and backup status. [E1] Acceptance signal: an imported folder round-trips without changing file names or note content.

### P1

Add a local search index with file-path provenance. [E1] Acceptance signal: every result opens its source file and line context.

### P2

Evaluate sharing after local recovery and import workflows are proven. [E2] Acceptance signal: five target users complete a sharing prototype without losing local ownership.

## Research Limits and Next Validation

This is desk research, not a usability study or an installation test. Validate import, backup, and search with five target users before treating local ownership as a proven differentiator.
