import csv
import math
import statistics
from pathlib import Path
from collections import defaultdict

results = Path("results")

# Load full CRP responses
responses = defaultdict(dict)

with (results / "full_crp_responses.csv").open(
    newline="", encoding="utf-8-sig"
) as f:
    for row in csv.DictReader(f):
        responses[int(row["crp_id"])][int(row["device_id"])] = (
            row["response_bits"]
        )

distances = []

for crp_id, device_responses in responses.items():
    device_ids = sorted(device_responses)

    for i in range(len(device_ids)):
        for j in range(i + 1, len(device_ids)):
            a = device_responses[device_ids[i]]
            b = device_responses[device_ids[j]]
            distances.append(sum(x != y for x, y in zip(a, b)))

total_bits = sum(
    len(response)
    for group in responses.values()
    for response in group.values()
)

ones = sum(
    response.count("1")
    for group in responses.values()
    for response in group.values()
)

p = ones / total_bits
randomness = -100 * math.log2(max(p, 1 - p))

print("========== FULL CRP METRIC AUDIT ==========")
print("CRPs:", len(responses))
print("Devices per CRP:", len(next(iter(responses.values()))))
print("Total response bits:", total_bits)
print(f"Uniformity (ones): {100*p:.6f}%")
print(f"Randomness:        {randomness:.6f}%")
print(
    f"Uniqueness:        "
    f"{100 * statistics.mean(distances) / 128:.6f}%"
)

# Minimum entropy summary
with (results / "minimum_entropy_results.csv").open(
    newline="", encoding="utf-8-sig"
) as f:
    entropy = [
        float(row["minimum_entropy"])
        for row in csv.DictReader(f)
    ]

print("\n========== MINIMUM ENTROPY AUDIT ==========")
print("CRPs:", len(entropy))
print(f"Mean: {statistics.mean(entropy):.6f}")
print(f"Population SD: {statistics.pstdev(entropy):.6f}")

# Check response dimensions and device count
assert len(responses) == 10000
assert all(len(group) == 5 for group in responses.values())
assert all(
    len(response) == 128
    for group in responses.values()
    for response in group.values()
)
assert len(entropy) == 10000

print("\nTEST_RESULT: PASS")
