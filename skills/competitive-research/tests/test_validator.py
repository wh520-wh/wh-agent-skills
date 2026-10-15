from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "check_competitive_report.py"
EXAMPLES = ROOT / "examples"
FIXTURES = ROOT / "tests" / "fixtures"


class ValidatorTests(unittest.TestCase):
    def run_validator(self, report: Path, ledger: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(report), str(ledger)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_accepts_complete_example(self) -> None:
        result = self.run_validator(EXAMPLES / "minimal-report.md", EXAMPLES / "minimal-ledger.json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS:", result.stdout)

    def test_rejects_invalid_evidence_and_report(self) -> None:
        result = self.run_validator(FIXTURES / "invalid-report.md", FIXTURES / "invalid-ledger.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL", result.stdout)
        self.assertIn("not an approved primary-source type", result.stdout)
        self.assertIn("unknown evidence id", result.stdout)


if __name__ == "__main__":
    unittest.main()
