#!/usr/bin/env python3
"""Validate a competitive-research Markdown report and evidence ledger."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


SOURCE_TYPES = {
    "official_product",
    "official_docs",
    "official_pricing",
    "official_release",
    "source_code",
    "official_paper",
    "official_presentation",
    "marketplace_listing",
    "package_registry",
}
PRIORITIES = {"P0", "P1", "P2"}
REQUIRED_HEADINGS = {
    "Executive Conclusion",
    "Competitor Comparison",
    "Prioritized Roadmap",
    "Research Limits and Next Validation",
}


def issue(errors: list[str], message: str) -> None:
    errors.append(message)


def valid_https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def read_ledger(path: Path, errors: list[str]) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issue(errors, f"Cannot read ledger: {exc}")
        return {}
    if not isinstance(data, dict):
        issue(errors, "Ledger root must be a JSON object.")
        return {}
    return data


def validate_evidence(ledger: dict, errors: list[str]) -> set[str]:
    evidence = ledger.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        issue(errors, "Ledger must contain a nonempty evidence array.")
        return set()

    ids: set[str] = set()
    for index, item in enumerate(evidence, start=1):
        prefix = f"evidence[{index}]"
        if not isinstance(item, dict):
            issue(errors, f"{prefix} must be an object.")
            continue
        evidence_id = item.get("id")
        if not isinstance(evidence_id, str) or not re.fullmatch(r"E[1-9][0-9]*", evidence_id):
            issue(errors, f"{prefix}.id must be E followed by a positive integer.")
        elif evidence_id in ids:
            issue(errors, f"Duplicate evidence id: {evidence_id}.")
        else:
            ids.add(evidence_id)
        for key in ("competitor", "claim", "accessed_on", "evidence_locator"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                issue(errors, f"{prefix}.{key} must be a nonempty string.")
        if not valid_https_url(item.get("source_url")):
            issue(errors, f"{prefix}.source_url must be an https URL.")
        if item.get("source_type") not in SOURCE_TYPES:
            issue(errors, f"{prefix}.source_type is not an approved primary-source type.")
        classification = item.get("classification")
        if classification not in {"fact", "inference"}:
            issue(errors, f"{prefix}.classification must be fact or inference.")
        elif classification == "inference" and "inference" not in item.get("claim", "").lower():
            issue(errors, f"{prefix} inference claim must say that it is an inference.")
        if item.get("confidence") not in {"high", "medium", "low"}:
            issue(errors, f"{prefix}.confidence must be high, medium, or low.")
    return ids


def validate_recommendations(ledger: dict, evidence_ids: set[str], errors: list[str]) -> None:
    recommendations = ledger.get("recommendations")
    if not isinstance(recommendations, list) or not recommendations:
        issue(errors, "Ledger must contain a nonempty recommendations array.")
        return
    found: set[str] = set()
    for index, item in enumerate(recommendations, start=1):
        prefix = f"recommendations[{index}]"
        if not isinstance(item, dict):
            issue(errors, f"{prefix} must be an object.")
            continue
        priority = item.get("priority")
        if priority not in PRIORITIES:
            issue(errors, f"{prefix}.priority must be P0, P1, or P2.")
        else:
            found.add(priority)
        for key in ("id", "statement", "acceptance_signal"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                issue(errors, f"{prefix}.{key} must be a nonempty string.")
        evidence_refs = item.get("evidence_ids")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            issue(errors, f"{prefix}.evidence_ids must be a nonempty array.")
        elif any(ref not in evidence_ids for ref in evidence_refs):
            issue(errors, f"{prefix}.evidence_ids references an unknown evidence id.")
    missing = PRIORITIES - found
    if missing:
        issue(errors, "Recommendations missing priority tiers: " + ", ".join(sorted(missing)) + ".")


def validate_report(path: Path, evidence_ids: set[str], errors: list[str]) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        issue(errors, f"Cannot read report: {exc}")
        return
    for heading in REQUIRED_HEADINGS:
        if f"## {heading}" not in content:
            issue(errors, f"Report missing required heading: {heading}.")
    for priority in sorted(PRIORITIES):
        if f"### {priority}" not in content:
            issue(errors, f"Report missing roadmap heading: {priority}.")
    if not re.search(r"non-goal|non goal", content, re.IGNORECASE):
        issue(errors, "Report must state at least one non-goal.")
    cited = set(re.findall(r"\[\s*(E[1-9][0-9]*)\s*\]", content))
    if not cited:
        issue(errors, "Report must cite at least one evidence id such as [E1].")
    unknown = cited - evidence_ids
    if unknown:
        issue(errors, "Report cites unknown evidence ids: " + ", ".join(sorted(unknown)) + ".")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: check_competitive_report.py <report.md> <ledger.json>")
        return 2
    report_path, ledger_path = Path(argv[1]), Path(argv[2])
    errors: list[str] = []
    ledger = read_ledger(ledger_path, errors)
    if not isinstance(ledger.get("research_date"), str) or not ledger.get("research_date"):
        issue(errors, "Ledger must include a nonempty research_date.")
    evidence_ids = validate_evidence(ledger, errors)
    validate_recommendations(ledger, evidence_ids, errors)
    validate_report(report_path, evidence_ids, errors)
    if errors:
        print("FAIL")
        for message in errors:
            print(f"- {message}")
        return 1
    print("PASS: report and evidence ledger satisfy the competitive-research contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
