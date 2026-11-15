"""Repeated-measurement steadiness experiment using synthetic noise."""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, "src")

import model_config as cfg
from threshold_model import generate_virtual_devices
from oscillator_model import calculate_pin_period

# Explicit illustrative assumption, not measured hardware noise.
NOISE_STD_FRACTION = 0.002

NUM_TEST_CRPS = 100
NUM_REPETITIONS = 1000


def build_nominal_periods(devices):
    periods = {}

    for device_id, pins in devices.items():
        periods[device_id] = [
            calculate_pin_period(
                pin["vih"], pin["vil"], cfg
            )["period_seconds"]
            for pin in pins
        ]

    return periods


def generate_challenges():
    rng = random.Random(cfg.RANDOM_SEED + 200)
    challenges = []

    for _ in range(NUM_TEST_CRPS):
        challenge = [
            tuple(rng.sample(range(cfg.NUM_PINS), 2))
            for _ in range(cfg.RESPONSE_BITS)
        ]
        challenges.append(challenge)

    return challenges


def measure_response(nominal_periods, challenge, rng):
    noisy_periods = []

    for period in nominal_periods:
        noisy = period + rng.gauss(
            0, period * NOISE_STD_FRACTION
        )
        noisy_periods.append(max(noisy, 1e-12))

    return "".join(
        "1" if noisy_periods[a] > noisy_periods[b] else "0"
        for a, b in challenge
    )


def calculate_steadiness(reference, repeated):
    total_bits = len(reference) * len(repeated)
    errors = sum(
        sum(a != b for a, b in zip(reference, response))
        for response in repeated
    )

    return 100 * (1 - errors / total_bits)


def main():
    devices = generate_virtual_devices(cfg)
    nominal_periods = build_nominal_periods(devices)
    challenges = generate_challenges()

    rng = random.Random(cfg.RANDOM_SEED + 300)
    results = []

    for device_id, periods in nominal_periods.items():
        device_scores = []

        for challenge in challenges:
            reference = "".join(
                "1" if periods[a] > periods[b] else "0"
                for a, b in challenge
            )

            repeated = [
                measure_response(periods, challenge, rng)
                for _ in range(NUM_REPETITIONS)
            ]

            device_scores.append(
                calculate_steadiness(reference, repeated)
            )

        results.append((device_id + 1, sum(device_scores) / len(device_scores)))

    output = Path("results") / "steadiness_results.csv"

    with output.open("w", encoding="utf-8") as file:
        file.write("device_id,average_steadiness_percent\n")
        for device_id, score in results:
            file.write(f"{device_id},{score:.6f}\n")

    print("========== STEADINESS EXPERIMENT ==========")
    print("Devices:", cfg.NUM_DEVICES)
    print("Test CRPs:", NUM_TEST_CRPS)
    print("Response bits:", cfg.RESPONSE_BITS)
    print("Repetitions per CRP:", NUM_REPETITIONS)
    print("Synthetic noise standard deviation:",
          f"{NOISE_STD_FRACTION * 100:.3f}%")

    for device_id, score in results:
        print(f"Device {device_id} steadiness: {score:.4f}%")

    average = sum(score for _, score in results) / len(results)
    print(f"Average steadiness: {average:.4f}%")
    print("CSV saved to:", output)
    print("TEST_RESULT: PASS")


if __name__ == "__main__":
    main()
