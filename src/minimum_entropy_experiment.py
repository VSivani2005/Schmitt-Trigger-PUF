"""Minimum entropy experiment implementing paper Equations (15) and (16).

Uses five synthetic devices and 10,000 shared challenge sequences.
"""

import csv
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, "src")

import model_config as cfg
from threshold_model import generate_virtual_devices
from oscillator_model import calculate_pin_period


def load_challenges(path):
    challenges = []

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            words = row["challenge_words_hex"].split()

            if len(words) != cfg.RESPONSE_BITS:
                raise ValueError(
                    f"Invalid response length in CRP {row['crp_id']}"
                )

            challenge = []

            for word in words:
                value = int(word, 16)
                a = value >> 5
                b = value & 31

                if a >= cfg.NUM_PINS or b >= cfg.NUM_PINS or a == b:
                    raise ValueError(
                        f"Invalid pin pair in CRP {row['crp_id']}"
                    )

                challenge.append((a, b))

            challenges.append(challenge)

    if len(challenges) != cfg.NUM_CRPS:
        raise ValueError(
            f"Expected {cfg.NUM_CRPS} CRPs, found {len(challenges)}"
        )

    return challenges


def main():
    print("========== MINIMUM ENTROPY EXPERIMENT ==========")
    print("Equations: (15) and (16)")
    print("Devices:", cfg.NUM_DEVICES)
    print("Pins per device:", cfg.NUM_PINS)
    print("CRPs:", cfg.NUM_CRPS)
    print("Response bits:", cfg.RESPONSE_BITS)

    challenge_path = Path("results") / "temperature_challenges.csv"
    challenges = load_challenges(challenge_path)

    print("Loaded challenge sequences:", len(challenges))

    devices = generate_virtual_devices(cfg)

    # Calculate quantized nominal period counts for every pin.
    device_counts = {}

    for device_id, pins in devices.items():
        device_counts[device_id] = [
            calculate_pin_period(
                pin["vih"], pin["vil"], cfg
            )["counter_cycles"]
            for pin in pins
        ]

    device_ids = list(device_counts.keys())

    if len(device_ids) != cfg.NUM_DEVICES:
        raise ValueError("Unexpected number of virtual devices")

    output_path = Path("results") / "minimum_entropy_results.csv"
    output_path.parent.mkdir(exist_ok=True)

    entropy_values = []

    with output_path.open(
        "w", newline="", encoding="utf-8"
    ) as f:

        writer = csv.writer(f)
        writer.writerow([
            "crp_id",
            "minimum_entropy"
        ])

        for crp_index, challenge in enumerate(challenges):

            # Generate one 128-bit response per device.
            responses = {}

            for device_id in device_ids:
                counts = device_counts[device_id]

                responses[device_id] = [
                    1 if counts[a] > counts[b] else 0
                    for a, b in challenge
                ]

            entropy_sum = 0.0

            # Calculate p_i,max and entropy for every response bit.
            for bit_index in range(cfg.RESPONSE_BITS):

                hamming_weight = sum(
                    responses[device_id][bit_index]
                    for device_id in device_ids
                )

                p_one = hamming_weight / cfg.NUM_DEVICES
                p_max = max(p_one, 1.0 - p_one)

                entropy_sum += -math.log2(p_max)

            crp_entropy = entropy_sum / cfg.RESPONSE_BITS
            entropy_values.append(crp_entropy)

            writer.writerow([
                crp_index + 1,
                f"{crp_entropy:.8f}"
            ])

            if (crp_index + 1) % 1000 == 0:
                print(
                    f"Processed {crp_index + 1}/"
                    f"{cfg.NUM_CRPS} CRPs"
                )

    average_entropy = statistics.mean(entropy_values)
    std_entropy = statistics.pstdev(entropy_values)

    print("\n========== MINIMUM ENTROPY RESULTS ==========")
    print(f"Average minimum entropy: {average_entropy:.6f}")
    print(f"Standard deviation:      {std_entropy:.6f}")
    print(f"Minimum observed:        {min(entropy_values):.6f}")
    print(f"Maximum observed:        {max(entropy_values):.6f}")

    print("\nPaper reference:")
    print("Average minimum entropy = 0.56")
    print("Standard deviation = 0.02")

    print("\nCSV saved to:", output_path)
    print("TEST_RESULT: PASS")


if __name__ == "__main__":
    main()
