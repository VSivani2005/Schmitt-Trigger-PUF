"""Exact entropy-based steadiness calculation using paper Equation (9).

All noise parameters are synthetic assumptions, not measured FPGA data.
"""

import math
import random
import sys
import csv
from pathlib import Path

sys.path.insert(0, "src")

import model_config as cfg
from threshold_model import generate_virtual_devices
from oscillator_model import calculate_pin_period

NOISE_STD_FRACTION = 0.002
AVERAGING_COUNT = 1000
NUM_TEST_CRPS = 100
NUM_REPETITIONS = 1000


def main():
    rng = random.Random(cfg.RANDOM_SEED + 700)

    devices = generate_virtual_devices(cfg)

    # Calculate nominal oscillator periods.
    nominal = {
        device_id: [
            calculate_pin_period(
                pin["vih"], pin["vil"], cfg
            )["period_seconds"]
            for pin in pins
        ]
        for device_id, pins in devices.items()
    }

    # Standard deviation of an average of independent Gaussian samples.
    def measure_average(period):
        std = (
            period * NOISE_STD_FRACTION
            / math.sqrt(AVERAGING_COUNT)
        )
        return rng.gauss(period, std)

    challenge_rng = random.Random(cfg.RANDOM_SEED + 701)

    challenges = [
        [
            tuple(challenge_rng.sample(range(cfg.NUM_PINS), 2))
            for _ in range(cfg.RESPONSE_BITS)
        ]
        for _ in range(NUM_TEST_CRPS)
    ]

    results = []

    print("========== EXACT STEADINESS EXPERIMENT ==========")
    print("Equation: Paper Equation (9)")
    print("Devices:", cfg.NUM_DEVICES)
    print("Test CRPs:", NUM_TEST_CRPS)
    print("Response bits:", cfg.RESPONSE_BITS)
    print("Repetitions:", NUM_REPETITIONS)
    print("Period averaging count:", AVERAGING_COUNT)
    print("Synthetic noise:", NOISE_STD_FRACTION * 100, "%")
    print()

    for device_id, periods in nominal.items():

        # Count the number of ones for each CRP response bit.
        ones = [
            [0] * cfg.RESPONSE_BITS
            for _ in range(NUM_TEST_CRPS)
        ]

        for repetition in range(NUM_REPETITIONS):

            measured_periods = [
                measure_average(period)
                for period in periods
            ]

            for crp_index, challenge in enumerate(challenges):
                for bit_index, (a, b) in enumerate(challenge):
                    if measured_periods[a] > measured_periods[b]:
                        ones[crp_index][bit_index] += 1

        log_sum = 0.0

        for crp_index in range(NUM_TEST_CRPS):
            for bit_index in range(cfg.RESPONSE_BITS):
                p = (
                    ones[crp_index][bit_index]
                    / NUM_REPETITIONS
                )

                dominant_probability = max(p, 1.0 - p)
                log_sum += math.log2(dominant_probability)

        mean_log = log_sum / (
            NUM_TEST_CRPS * cfg.RESPONSE_BITS
        )

        steadiness = 100.0 * (1.0 + mean_log)

        results.append((device_id, steadiness))

        print(
            f"Device {device_id}: "
            f"Steadiness = {steadiness:.6f}%"
        )

    average = sum(value for _, value in results) / len(results)

    output = Path("results") / "exact_steadiness_results.csv"
    output.parent.mkdir(exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["device_id", "steadiness_percent"])

        for device_id, value in results:
            writer.writerow([device_id, f"{value:.8f}"])

        writer.writerow(["AVERAGE", f"{average:.8f}"])

    print()
    print(f"Average steadiness: {average:.6f}%")
    print("CSV saved to:", output)
    print("TEST_RESULT: PASS")


if __name__ == "__main__":
    main()
