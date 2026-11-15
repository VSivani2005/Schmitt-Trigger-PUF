import csv
from pathlib import Path

folder = Path("results")

print("=" * 75)
print("SCHMITT-TRIGGER PUF — RESULT FILE AUDIT")
print("=" * 75)

for path in sorted(folder.glob("*.csv")):
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        rows = list(reader)

    print(f"\nFile: {path.name}")
    print(f"Columns: {header}")
    print(f"Data rows: {len(rows)}")

    if rows:
        print(f"First record: {rows[0]}")
        print(f"Last record:  {rows[-1]}")

print("\n" + "=" * 75)
print("AUDIT LISTING COMPLETE")
