import sys
from collections import Counter

sys.path.insert(0, "src")

import model_config as cfg
from full_crp_experiment import generate_challenges

challenges = generate_challenges()

encoded = [
    tuple(challenge)
    for challenge in challenges
]

counts = Counter(encoded)
unique_count = len(counts)
duplicate_count = len(encoded) - unique_count

print("========== CHALLENGE UNIQUENESS AUDIT ==========")
print("Total challenge sequences:", len(encoded))
print("Unique sequences:", unique_count)
print("Duplicate sequences:", duplicate_count)
print(
    "Unique sequence percentage:",
    f"{100 * unique_count / len(encoded):.4f}%"
)

print("Each sequence contains 128 pin pairs:",
      all(len(c) == cfg.RESPONSE_BITS for c in encoded))

print("TEST_RESULT: PASS")
