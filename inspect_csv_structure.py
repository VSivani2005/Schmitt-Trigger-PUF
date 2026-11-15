import csv
from pathlib import Path

files = [
    "full_crp_responses.csv",
    "temperature_challenges.csv",
    "minimum_entropy_results.csv",
    "temperature_reliability_results.csv",
    "error_probability_results.csv",
    "exact_steadiness_results.csv",
    "averaging_results.csv",
]

print("========== CSV STRUCTURE AUDIT ==========")

for filename in files:
    path = Path("results") / filename
    print(f"\n--- {filename} ---")

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        first_row = next(reader, None)

    print("Header:", header)
    print("First row:", first_row)
