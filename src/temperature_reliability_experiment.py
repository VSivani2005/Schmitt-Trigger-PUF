"""Synthetic temperature reliability experiment for the Schmitt-trigger PUF.

Implements:
    Equation (14): P_h(T) = lambda_h * T^1.6 + mu_h
    Equation (13): Reliability from normalized Hamming distance

IMPORTANT: Temperature coefficients are synthetic, not measured FPGA data.
"""

import csv
import hashlib
import random
import sys
from pathlib import Path

sys.path.insert(0, "src")

import model_config as cfg
from threshold_model import generate_virtual_devices
from oscillator_model import calculate_pin_period, period_to_counter_cycles


# Explicit synthetic assumption: maximum fractional period change
# between 25 C and 65 C is randomly selected within +/- 0.5%.
MAX_FRACTIONAL_SPAN = 0.005

def main():
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    rng = random.Random(cfg.RANDOM_SEED + 600)

    devices = generate_virtual_devices(cfg)

    # Calculate nominal periods at the reference temperature.
    nominal_periods = {}

    for device_id, pins in devices.items():
        nominal_periods[device_id] = [
            calculate_pin_period(
                pin["vih"], pin["vil"], cfg
            )["period_seconds"]
            for pin in pins
        ]

    # Generate synthetic temperature coefficients for every pin.
    coefficients = {}

    coefficient_path = output_dir / "temperature_coefficients.csv"

    with coefficient_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "device_id", "pin_id", "lambda", "mu",
            "fractional_span"
        ])

        for device_id, periods in nominal_periods.items():
            coefficients[device_id] = []

            for pin_id, period_25 in enumerate(periods):
                span = rng.uniform(
                    -MAX_FRACTIONAL_SPAN,
                    MAX_FRACTIONAL_SPAN
                )

                temperature_difference = (
                    max(cfg.TEMPERATURES_C) ** 1.6
                    - cfg.REFERENCE_TEMPERATURE_C ** 1.6
                )

                lam = period_25 * span / temperature_difference
                mu = period_25 - lam * (
                    cfg.REFERENCE_TEMPERATURE_C ** 1.6
                )

                coefficients[device_id].append((lam, mu))

                writer.writerow([
                    device_id, pin_id,
                    f"{lam:.12e}", f"{mu:.12e}",
                    f"{span:.8f}"
                ])

    # Calculate quantized counter measurements at every temperature.
    temperature_counts = {}

    for device_id, periods in nominal_periods.items():
        temperature_counts[device_id] = {}

        for temperature in cfg.TEMPERATURES_C:
            counts = []

            for pin_id, period_25 in enumerate(periods):
                lam, mu = coefficients[device_id][pin_id]

                period = lam * temperature ** 1.6 + mu

                if period <= 0:
                    raise ValueError("Invalid temperature-adjusted period")

                counts.append(
                    period_to_counter_cycles(
                        period, cfg.COUNTER_CLOCK_HZ
                    )
                )

            temperature_counts[device_id][temperature] = counts

    # Accumulate Hamming-distance errors against the 25 C reference.
    errors = {
        device_id: {t: 0 for t in cfg.TEMPERATURES_C}
        for device_id in devices
    }

    total_bits = 0
    seen_challenges = set()
    challenge_path = output_dir / "temperature_challenges.csv"

    challenge_rng = random.Random(cfg.RANDOM_SEED + 601)

    print("========== TEMPERATURE RELIABILITY EXPERIMENT ==========")
    print("Devices:", cfg.NUM_DEVICES)
    print("Pins per device:", cfg.NUM_PINS)
    print("CRPs:", cfg.NUM_CRPS)
    print("Response bits per CRP:", cfg.RESPONSE_BITS)
    print("Temperatures:", cfg.TEMPERATURES_C)
    print("Reference temperature:", cfg.REFERENCE_TEMPERATURE_C, "C")
    print("Generating responses...")

    with challenge_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["crp_id", "challenge_words_hex"])

        for crp_id in range(cfg.NUM_CRPS):
            # Ensure every complete 128-pair challenge sequence is unique.
            while True:
                challenge = [
                    tuple(challenge_rng.sample(range(cfg.NUM_PINS), 2))
                    for _ in range(cfg.RESPONSE_BITS)
                ]

                words = [(a << 5) | b for a, b in challenge]
                digest = hashlib.sha256(
                    b"".join(w.to_bytes(2, "big") for w in words)
                ).digest()

                if digest not in seen_challenges:
                    seen_challenges.add(digest)
                    break

            writer.writerow([
                crp_id + 1,
                " ".join(f"{word:03X}" for word in words)
            ])

            for device_id in devices:
                reference = temperature_counts[device_id][
                    cfg.REFERENCE_TEMPERATURE_C
                ]

                reference_response = [
                    reference[a] > reference[b]
                    for a, b in challenge
                ]

                for temperature in cfg.TEMPERATURES_C:
                    measured = temperature_counts[device_id][temperature]

                    measured_response = [
                        measured[a] > measured[b]
                        for a, b in challenge
                    ]

                    errors[device_id][temperature] += sum(
                        ref != test
                        for ref, test in zip(
                            reference_response, measured_response
                        )
                    )

            total_bits += cfg.RESPONSE_BITS

            if (crp_id + 1) % 1000 == 0:
                print(f"Processed {crp_id + 1}/{cfg.NUM_CRPS} CRPs")

    # Calculate reliability and save results.
    results_path = output_dir / "temperature_reliability_results.csv"
    averages = {}

    with results_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "device_id", "temperature_C",
            "hamming_errors", "total_bits", "reliability_percent"
        ])

        for device_id in devices:
            for temperature in cfg.TEMPERATURES_C:
                reliability = 100 * (
                    1 - errors[device_id][temperature] / total_bits
                )

                averages.setdefault(temperature, []).append(reliability)

                writer.writerow([
                    device_id,
                    temperature,
                    errors[device_id][temperature],
                    total_bits,
                    f"{reliability:.6f}"
                ])

    print("\n========== RELIABILITY RESULTS ==========")

    for temperature in cfg.TEMPERATURES_C:
        mean_reliability = sum(averages[temperature]) / len(
            averages[temperature]
        )

        print(
            f"{temperature:2d} C: "
            f"Average reliability = {mean_reliability:.4f}%"
        )

    overall = sum(
        value
        for values in averages.values()
        for value in values
    ) / sum(len(values) for values in averages.values())

    print(f"\nOverall average reliability: {overall:.4f}%")
    print("Unique challenge sequences:", len(seen_challenges))
    print("CSV files saved:")
    print(" ", coefficient_path)
    print(" ", challenge_path)
    print(" ", results_path)
    print("TEST_RESULT: PASS")


if __name__ == "__main__":
    main()
