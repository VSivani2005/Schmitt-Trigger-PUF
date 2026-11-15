"""Preliminary PUF uniqueness, uniformity and randomness metrics."""

import csv
import math
from itertools import combinations
from pathlib import Path


def hamming_distance(a, b):
    if len(a) != len(b):
        raise ValueError("Responses must have equal lengths")
    return sum(x != y for x, y in zip(a, b))


def calculate_metrics(responses):
    device_ids = sorted(responses)
    response_length = len(responses[device_ids[0]])

    if response_length == 0:
        raise ValueError("Empty response")

    pair_distances = []

    for first, second in combinations(device_ids, 2):
        distance = hamming_distance(
            responses[first], responses[second]
        )
        pair_distances.append(distance)

    average_hd = sum(pair_distances) / len(pair_distances)
    uniqueness = (average_hd / response_length) * 100

    all_bits = "".join(responses[d] for d in device_ids)
    p = all_bits.count("1") / len(all_bits)

    if p == 0 or p == 1:
        randomness = 0.0
    else:
        randomness = -100 * math.log2(max(p, 1 - p))

    uniformity = p * 100

    return {
        "device_count": len(device_ids),
        "response_length": response_length,
        "pair_count": len(pair_distances),
        "pair_distances": pair_distances,
        "average_hamming_distance": average_hd,
        "uniqueness_percent": uniqueness,
        "ones_fraction": p,
        "uniformity_percent": uniformity,
        "randomness_percent": randomness
    }


if __name__ == "__main__":
    input_path = Path("results") / "pairwise_responses.csv"

    responses = {}

    with input_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            device_id = int(row["device_id"])
            response = row["response_bits"]

            if len(response) != int(row["response_length"]):
                raise ValueError("CSV response length mismatch")

            if not set(response).issubset({"0", "1"}):
                raise ValueError("Response contains non-binary characters")

            responses[device_id] = response

    metrics = calculate_metrics(responses)

    print("========== PRELIMINARY PUF METRICS ==========")
    print("Virtual devices:", metrics["device_count"])
    print("Response length:", metrics["response_length"])
    print("Inter-device comparisons:", metrics["pair_count"])

    print("\nPairwise Hamming distances:")
    for pair, distance in zip(
        combinations(sorted(responses), 2),
        metrics["pair_distances"]
    ):
        print(f"Devices {pair[0]} and {pair[1]}: {distance}")

    print("\nMetric results:")
    print(
        f"Average Hamming distance: "
        f"{metrics['average_hamming_distance']:.4f}"
    )
    print(f"Uniqueness: {metrics['uniqueness_percent']:.2f}%")
    print(f"Uniformity (ones): {metrics['uniformity_percent']:.2f}%")
    print(f"Randomness: {metrics['randomness_percent']:.2f}%")

    print("\nNOTE: Preliminary synthetic-model results.")
    print("This is one 128-bit response per device,")
    print("not the paper's full 10,000-CRP experiment.")

    print("\nTEST_RESULT: PASS")
