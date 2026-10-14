"""Local schema validation; aggregation and plotting belong to Code Interpreter."""

import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import io
from pathlib import Path
import re


def revenue(value: str) -> Decimal:
    try:
        amount = Decimal(value)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("revenue_eur must be numeric.") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError("revenue_eur must be finite and nonnegative.")
    return amount


def validate_rows(text: str, *, totals: bool = False) -> int:
    reader = csv.DictReader(io.StringIO(text))
    required = {"month", "revenue_eur"} if totals else {"month", "category", "orders", "revenue_eur"}
    fields = reader.fieldnames or []
    if not required.issubset(fields) or len(fields) != len(set(fields)):
        raise ValueError(f"CSV requires distinct columns including: {', '.join(sorted(required))}.")
    seen_months = set()
    count = 0
    for count, row in enumerate(reader, start=1):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"CSV row {count} has a different number of columns than its header.")
        month = row["month"]
        if not re.fullmatch(r"\d{4}-\d{2}", month):
            raise ValueError(f"CSV row {count}: month must use YYYY-MM.")
        datetime.strptime(month, "%Y-%m")
        revenue(row["revenue_eur"])
        if totals:
            if month in seen_months:
                raise ValueError("Monthly totals must have one row per month.")
            seen_months.add(month)
        elif not row["category"].strip() or not re.fullmatch(r"\d+", row["orders"]):
            raise ValueError(f"CSV row {count}: category is required; orders must be a nonnegative integer.")
    if count == 0:
        raise ValueError("CSV must contain at least one data row.")
    return count


def validate_input(path: Path) -> int:
    if path.suffix.lower() != ".csv":
        raise ValueError("Input must be a .csv file.")
    return validate_rows(path.read_text(encoding="utf-8-sig"))
