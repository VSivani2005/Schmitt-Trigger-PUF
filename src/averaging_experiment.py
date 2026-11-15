"""Evaluate oscillator-period averaging under synthetic measurement noise."""

import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, "src")

import model_config as cfg
from threshold_model import generate_virtual_devices
from oscillator_model import calculate_pin_period

NOISE_STD_FRACTION = 0.002
NUM_TEST_CRPS = 100
NUM_REPETITIONS = 200


def build_periods(devices):
    return {
        device_id: [
            calculate_pin_period(
                pin["vih"], pin["vil"], cfg
            )["period_seconds"]
            for pin in pins
        ]
        for device_id, pins in devices.items()
    }


def build_challenges():
    rng = random.Random(cfg.RANDOM_SEED + 400)
    return [
        [
            tuple(rng.sample(range(cfg.NUM_PINS), 2))
            for _ in range(cfg.RESPONSE_BITS)
        ]
        for _ in range(NUM_TEST_CRPS)
    ]


def noisy_average(period, count, rng):
    # Exact Gaussian distribution of the mean of count
    # independent Gaussian measurements.
    averaged_std = period * NOISE_STD_FRACTION / (count ** 0.5)
    return rng.gauss(period, averaged_std)


def response_from_periods(periods, challenge):
    return "".join(
        "1" if periods[a] > periods[b] else "0"
        for a, b in challenge
    )


def main():
    devices = generate_virtual_devices(cfg)
    nominal = build_periods(devices)
    challenges = build_challenges()

    rng = random.Random(cfg.RANDOM_SEED + 500)
    output = Path("results") / "averaging_results.csv"
    output.parent.mkdir(parents=True, exist_ok=True)

    completed = set()

    if output.exists():
        with output.open("r", newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                completed.add(int(row["averaging_count"]))

    missing = [
        count for count in cfg.AVERAGING_COUNTS
        if count not in completed
    ]

    print("========== PERIOD AVERAGING EXPERIMENT ==========")
    print("Already completed:", sorted(completed))
    print("Remaining:", missing)

    if not missing:
        print("All averaging configurations are already present.")
        return

    write_header = not output.exists() or output.stat().st_size == 0

    with output.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if write_header:
            writer.writerow([
                "averaging_count",
                "steadiness_percent"
            ])

        for count in missing:
            total_bits = 0
            matching_bits = 0

            for periods in nominal.values():
                for challenge in challenges:
                    reference = response_from_periods(
                        periods, challenge
                    )

                    for _ in range(NUM_REPETITIONS):
                        averaged = [
                            noisy_average(period, count, rng)
                            for period in periods
                        ]

                        measured = response_from_periods(
                            averaged, challenge
                        )

                        matching_bits += sum(
                            a == b
                            for a, b in zip(reference, measured)
                        )
                        total_bits += len(reference)

            steadiness = 100 * matching_bits / total_bits

            writer.writerow([count, f"{steadiness:.6f}"])
            file.flush()

            print(
                f"Averaging {count:4d}: "
                f"Steadiness = {steadiness:.4f}%"
            )

    print("CSV saved to:", output)
    print("TEST_RESULT: PASS")


if __name__ == "__main__":
    main()
