"""Full 10,000-CRP experiment using the canonical saved challenge dataset."""

import csv
import math
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, "src")

import model_config as cfg
from threshold_model import generate_virtual_devices
from oscillator_model import calculate_pin_period


def load_challenges(path):
    challenges = []
    seen = set()

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        required = {"crp_id", "challenge_words_hex"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Challenge CSV has an invalid header")

        for expected_id, row in enumerate(reader, start=1):
            if int(row["crp_id"]) != expected_id:
                raise ValueError(f"Unexpected CRP ID: {row['crp_id']}")

            words = row["challenge_words_hex"].split()

            if len(words) != cfg.RESPONSE_BITS:
                raise ValueError(
                    f"CRP {expected_id}: expected "
                    f"{cfg.RESPONSE_BITS} words, found {len(words)}"
                )

            challenge = []

            for word_hex in words:
                word = int(word_hex, 16)
                first = (word >> 5) & 0x1F
                second = word & 0x1F

                if first >= cfg.NUM_PINS or second >= cfg.NUM_PINS:
                    raise ValueError(
                        f"CRP {expected_id}: invalid pin pair {first}, {second}"
                    )

                if first == second:
                    raise ValueError(
                        f"CRP {expected_id}: identical pins in a pair"
                    )

                challenge.append((first, second))

            key = tuple(challenge)

            if key in seen:
                raise ValueError(f"Duplicate complete challenge at CRP {expected_id}")

            seen.add(key)
            challenges.append(challenge)

    if len(challenges) != cfg.NUM_CRPS:
        raise ValueError(
            f"Expected {cfg.NUM_CRPS} CRPs, found {len(challenges)}"
        )

    return challenges


def calculate_device_counts(devices):
    result = {}

    for device_id, pins in devices.items():
        result[device_id] = [
            calculate_pin_period(pin["vih"], pin["vil"], cfg)["counter_cycles"]
            for pin in pins
        ]

    return result


def calculate_response(counts, challenge):
    return "".join(
        "1" if counts[first] > counts[second] else "0"
        for first, second in challenge
    )


def hamming_distance(first, second):
    return sum(a != b for a, b in zip(first, second))


def main():
    challenge_path = Path("results") / "temperature_challenges.csv"
    output_path = Path("results") / "full_crp_responses.csv"

    challenges = load_challenges(challenge_path)

    devices = generate_virtual_devices(cfg)
    device_counts = calculate_device_counts(devices)

    pair_uniqueness_values = []
    total_ones = 0
    total_bits = 0

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["crp_id", "device_id", "response_bits"])

        for crp_id, challenge in enumerate(challenges, start=1):
            responses = {}

            for device_id, counts in device_counts.items():
                response = calculate_response(counts, challenge)
                responses[device_id] = response

                writer.writerow([crp_id, device_id + 1, response])

                total_ones += response.count("1")
                total_bits += len(response)

            distances = [
                hamming_distance(responses[a], responses[b])
                for a, b in combinations(sorted(responses), 2)
            ]

            pair_uniqueness_values.append(
                sum(distances) / len(distances) / cfg.RESPONSE_BITS
            )

    uniqueness = sum(pair_uniqueness_values) / len(pair_uniqueness_values) * 100

    p = total_ones / total_bits
    uniformity = p * 100
    randomness = (
        0.0 if p in (0, 1)
        else -100 * math.log2(max(p, 1 - p))
    )

    expected_rows = cfg.NUM_CRPS * cfg.NUM_DEVICES

    print("\n========== ALIGNED FULL CRP EXPERIMENT ==========")
    print("Challenge source:", challenge_path)
    print("Unique challenge sequences:", len(challenges))
    print("Virtual devices:", cfg.NUM_DEVICES)
    print("CRPs:", len(challenges))
    print("Response bits per CRP:", cfg.RESPONSE_BITS)
    print("Response rows:", expected_rows)
    print("Total response bits:", total_bits)
    print(f"Uniqueness: {uniqueness:.6f}%")
    print(f"Uniformity (ones): {uniformity:.6f}%")
    print(f"Randomness: {randomness:.6f}%")
    print("Output:", output_path)

    assert len(challenges) == cfg.NUM_CRPS
    assert len(challenges) == len(set(tuple(c) for c in challenges))
    assert total_bits == expected_rows * cfg.RESPONSE_BITS

    print("TEST_RESULT: PASS")


if __name__ == "__main__":
    main()
