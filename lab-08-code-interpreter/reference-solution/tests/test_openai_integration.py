"""Opt-in test of real hosted execution and downloaded chart data."""

from collections import defaultdict
import csv
from decimal import Decimal
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest

from artifacts import PNG_SIGNATURE
from generate_data import DEFAULT_CSV
from run_reference import main


class LiveCodeInterpreterTests(unittest.IsolatedAsyncioTestCase):
    async def test_csv_becomes_chart_with_correct_monthly_totals(self):
        if os.environ.get("RUN_CODE_INTERPRETER_SMOKE") != "1":
            self.skipTest("Set RUN_CODE_INTERPRETER_SMOKE=1 to opt into a live API run.")
        if not os.environ.get("OPENAI_API_KEY", "").strip():
            if os.environ.get("REQUIRE_OPENAI_API") == "1":
                self.fail("OPENAI_API_KEY is required for the requested live smoke test.")
            self.skipTest("OPENAI_API_KEY is missing or blank.")

        # Keep the actual generated chart for visual review, even after a test failure.
        output = Path(tempfile.mkdtemp(prefix="lab08-code-interpreter-"))
        print(f"Live test output parent (retained): {output}", flush=True)
        status = await main(["run", "--csv", str(DEFAULT_CSV), "--output-dir", str(output)])
        self.assertEqual(status, 0, f"Inspect retained artifacts/resources under {output}")
        runs = list(output.glob("run-*"))
        self.assertEqual(len(runs), 1)
        folder = runs[0]
        self.assertFalse((folder / "resources.json").exists(), "Remote cleanup is incomplete.")
        report = json.loads((folder / "run-report.json").read_text())
        self.assertEqual(report["input_rows"], 36)
        self.assertTrue(any(call["status"] == "completed" and call["container_id"] == report["container_id"]
                            for call in report["code_interpreter_calls"]))
        png = (folder / "monthly_revenue.png").read_bytes()
        self.assertTrue(png.startswith(PNG_SIGNATURE))
        self.assertEqual(png[12:16], b"IHDR")
        width, height = struct.unpack(">II", png[16:24])
        self.assertGreaterEqual(width, 800)
        self.assertGreaterEqual(height, 450)

        # Independent deterministic oracle belongs in this test, not the agent flow.
        expected = defaultdict(Decimal)
        with DEFAULT_CSV.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                expected[row["month"]] += Decimal(row["revenue_eur"])
        with (folder / "monthly_totals.csv").open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(reader.fieldnames, ["month", "revenue_eur"])
            totals = list(reader)
        self.assertEqual([row["month"] for row in totals], sorted(expected))
        self.assertEqual({row["month"]: Decimal(row["revenue_eur"]) for row in totals}, dict(expected))
        print(f"Verified chart and totals. Open for visual review: {folder / 'monthly_revenue.png'}")


if __name__ == "__main__":
    unittest.main()
