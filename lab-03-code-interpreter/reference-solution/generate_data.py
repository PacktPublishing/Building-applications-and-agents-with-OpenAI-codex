"""Generate fictional CSV input only. The chart is created by hosted Code Interpreter."""

import csv
from pathlib import Path

DEFAULT_CSV = Path(__file__).resolve().parent / "data" / "sales.csv"
FIELDS = ("month", "category", "orders", "revenue_eur")
BASE_ORDERS = (120, 110, 140, 150, 170, 165, 155, 175, 180, 195, 220, 260)


def generate_csv(path: Path = DEFAULT_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(FIELDS)
        for month, base in enumerate(BASE_ORDERS, start=1):
            for category, orders, price in (
                ("Grocery", base, 22),
                ("Household", base // 2, 15),
                ("Personal care", base // 3, 12),
            ):
                writer.writerow((f"2025-{month:02d}", category, orders, f"{orders * price:.2f}"))


if __name__ == "__main__":
    generate_csv()
    print(f"Wrote 36 fictional sales rows to {DEFAULT_CSV}")
