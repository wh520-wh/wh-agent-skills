# Test Prompts

Run these prompts against a fresh agent after changing `SKILL.md` or the validator.

## Broad Market

> Find at least 12 competitors for a local-first AI writing application and recommend a roadmap.

Pass condition: declares Deep mode, distinguishes direct/adjacent/potential/baseline competitors, records primary sources, cites evidence IDs, names a non-goal, and provides P0/P1/P2 acceptance signals.

## Small Market

> Compare competitors for a niche offline screenplay formatter. There may be fewer than six credible products.

Pass condition: does not pad the list; explains the actual count and search boundary; lists unverified paths in limits.

## Local Material Only

> Analyze this repository's competitive position using its README and docs. Do not browse the web.

Pass condition: labels conclusions as local-product evidence and assumptions; does not invent external competitor claims.

## High-Stakes Choice

> Should we replace our self-hosted analytics product with a SaaS vendor next quarter?

Pass condition: declares Deep mode, marks pricing and security claims as date-sensitive, separates desk research from hands-on validation, and recommends an installation/security validation before the decision.
