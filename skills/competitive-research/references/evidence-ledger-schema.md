# Evidence Ledger Schema

Use JSON so the standard-library validator can check the artifact without dependencies.

```json
{
  "research_date": "YYYY-MM-DD",
  "evidence": [
    {
      "id": "E1",
      "competitor": "Example Product",
      "claim": "The official documentation states that ...",
      "source_url": "https://example.com/docs",
      "source_type": "official_docs",
      "accessed_on": "YYYY-MM-DD",
      "evidence_locator": "Section heading or source-file path",
      "classification": "fact",
      "confidence": "high"
    }
  ],
  "recommendations": [
    {
      "id": "R1",
      "priority": "P0",
      "statement": "Build the smallest coherent outcome.",
      "evidence_ids": ["E1"],
      "acceptance_signal": "A concrete observable pass condition."
    }
  ]
}
```

Rules:

- `id` values must be unique `E` or `R` identifiers.
- `source_type` must be one of `official_product`, `official_docs`, `official_pricing`, `official_release`, `source_code`, `official_paper`, `official_presentation`, `marketplace_listing`, or `package_registry`.
- `classification` is `fact` or `inference`. An inference must say that it is an inference in its `claim`.
- `confidence` is `high`, `medium`, or `low`.
- `evidence_locator` identifies the heading, page, release, or source path that supports the claim.
- Recommendations must cover P0, P1, and P2, cite existing evidence IDs, and include a nonempty acceptance signal.
