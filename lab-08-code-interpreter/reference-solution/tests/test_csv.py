import csv
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from csv_checks import validate_input, validate_rows
from generate_data import DEFAULT_CSV, generate_csv


class CsvTests(unittest.TestCase):
    def test_fixture_is_reproducible_and_valid(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "sales.csv"
            generate_csv(path)
            self.assertEqual(path.read_bytes(), DEFAULT_CSV.read_bytes())
            self.assertEqual(validate_input(path), 36)
        with DEFAULT_CSV.open() as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len({row["month"] for row in rows}), 12)
        for month, expected in (("2025-01", "4020.00"), ("2025-12", "8702.00")):
            self.assertEqual(sum(Decimal(row["revenue_eur"]) for row in rows if row["month"] == month),
                             Decimal(expected))

    def test_invalid_inputs_fail_before_upload(self):
        cases = (
            "month,revenue_eur\n2025-01,10\n",
            "month,category,orders,revenue_eur\n",
            "month,category,orders,revenue_eur\n2025-13,Food,1,10\n",
            "month,category,orders,revenue_eur\n2025-1,Food,1,10\n",
            "month,category,orders,revenue_eur\n2025-01,Food,-1,10\n",
            "month,category,orders,revenue_eur\n2025-01,Food,1,NaN\n",
            "month,category,orders,revenue_eur\n2025-01,Food,1,Infinity\n",
            "month,category,orders,revenue_eur\n2025-01,Food,1,-10\n",
            "month,category,orders,revenue_eur\n2025-01,,1,10\n",
            "month,category,orders,revenue_eur\n2025-01,Food,1\n",
        )
        for text in cases:
            with self.subTest(text=text), self.assertRaises(ValueError):
                validate_rows(text)

    def test_totals_reject_duplicate_months(self):
        with self.assertRaisesRegex(ValueError, "one row per month"):
            validate_rows("month,revenue_eur\n2025-01,10\n2025-01,20\n", totals=True)


if __name__ == "__main__":
    unittest.main()
