import time
import statistics
from pathlib import Path

from app.parser import load_financial_statement

FILES = [
    "data/microsoft_balance_sheet.csv",
    "data/nvidia_balance_sheet.xlsx",
    "data/apple_financial_statement_q4.pdf",
]

times = []

print("Parser Benchmark\n")

for file in FILES:
    path = Path(file)

    start = time.perf_counter()

    with open(path, "rb") as f:
        load_financial_statement(f)

    elapsed = time.perf_counter() - start
    times.append(elapsed)

    print(f"{path.name:<40}{elapsed:.2f}s")

print("\nSummary")
print("-" * 30)
print(f"Average : {statistics.mean(times):.2f}s")
print(f"Median  : {statistics.median(times):.2f}s")
print(f"Fastest : {min(times):.2f}s")
print(f"Slowest : {max(times):.2f}s")