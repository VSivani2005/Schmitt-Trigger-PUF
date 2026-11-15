import csv
from pathlib import Path

path = Path("results") / "full_crp_responses.csv"

records = {}
with path.open("r", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        crp = int(row["crp_id"])
        device = int(row["device_id"])
        records.setdefault(crp, set()).add(device)

print("CRPs in CSV:", len(records))
print("CRPs with all 5 device responses:",
      sum(len(devices) == 5 for devices in records.values()))
print("Expected records:", 10000 * 5)
print("Actual records:", sum(len(v) for v in records.values()))
