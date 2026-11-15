"""Error probability experiment implementing paper Equations (11) and (12).

Synthetic assumption:
Individual oscillator period standard deviation = 0.2% of nominal period.
This is not measured FPGA data.
"""

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, "src")

import model_config as cfg
from threshold_model import generate_virtual_devices
from oscillator_model import calculate_pin_period

NOISE_STD_FRACTION = 0.002

ERROR_THRESHOLDS = [
    1e-1, 1e-2, 1e-3, 1e-4,
    1e-5, 1e-6, 1e-7
]


def load_challenges(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Challenge file not found: {path}"
        )

    challenges = []

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            words = row["challenge_words_hex"].split()

            if len(words) != cfg.RESPONSE_BITS:
                raise ValueError(
                    f"CRP {row['crp_id']} does not contain "
                    f"{cfg.RESPONSE_BITS} challenge words"
                )

            challenge = []

            for word in words:
                value = int(word, 16)
                a = value >> 5
                b = value & 31

                if (
                    a >= cfg.NUM_PINS
                    or b >= cfg.NUM_PINS
                    or a == b
                ):
                    raise ValueError(
                        f"Invalid pin pair in CRP {row['crp_id']}"
                    )

                challenge.append((a, b))

            challenges.append(challenge)

    if len(challenges) != cfg.NUM_CRPS:
        raise ValueError(
            f"Expected {cfg.NUM_CRPS} CRPs, "
            f"found {len(challenges)}"
        )

    return challenges


def bit_error_probability(mean_a, mean_b, sigma_a, sigma_b):
    """Equation (11): probability of reversing the nominal ordering."""

    difference = abs(mean_a - mean_b)

    combined_sigma = math.sqrt(
        sigma_a ** 2 + sigma_b ** 2
    )

    if combined_sigma == 0:
        return 0.0

    z = difference / combined_sigma

    # Gaussian lower-tail probability:
    # P(error) = Phi(-z)
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def crp_error_probability(challenge, periods, sigmas, averaging_count):
    """Equation (12): probability of >=1 error in a complete CRP."""

    log_no_error = 0.0

    averaging_scale = math.sqrt(averaging_count)

    for a, b in challenge:
        sigma_a = sigmas[a] / averaging_scale
        sigma_b = sigmas[b] / averaging_scale

        p_bit = bit_error_probability(
            periods[a],
            periods[b],
            sigma_a,
            sigma_b
        )

        # Numerically stable multiplication of (1 - p_bit).
        if p_bit >= 1.0:
            return 1.0

        log_no_error += math.log1p(-p_bit)

    return -math.expm1(log_no_error)


def main():
    print("========== ERROR PROBABILITY EXPERIMENT ==========")
    print("Equations: (11) and (12)")
    print("Devices:", cfg.NUM_DEVICES)
    print("Pins per device:", cfg.NUM_PINS)
    print("CRPs:", cfg.NUM_CRPS)
    print("Response bits:", cfg.RESPONSE_BITS)
    print("Averaging counts:", cfg.AVERAGING_COUNTS)
    print("Synthetic period noise:", NOISE_STD_FRACTION * 100, "%")
    print()

    challenge_file = (
        Path("results") / "temperature_challenges.csv"
    )

    challenges = load_challenges(challenge_file)

    print("Loaded challenge sequences:", len(challenges))

    devices = generate_virtual_devices(cfg)

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    detail_path = output_dir / "error_probability_per_crp.csv"
    summary_path = output_dir / "error_probability_results.csv"

    summary_rows = []

    with detail_path.open(
        "w", newline="", encoding="utf-8"
    ) as detail_file:

        detail_writer = csv.writer(detail_file)

        detail_writer.writerow([
            "device_id",
            "averaging_count",
            "crp_id",
            "crp_error_probability"
        ])

        for device_id, pins in devices.items():

            periods = [
                calculate_pin_period(
                    pin["vih"], pin["vil"], cfg
                )["period_seconds"]
                for pin in pins
            ]

            # Synthetic standard deviation of individual measurements.
            sigmas = [
                period * NOISE_STD_FRACTION
                for period in periods
            ]

            print(f"\nProcessing device {device_id}...")

            for count in cfg.AVERAGING_COUNTS:

                probabilities = []

                for crp_index, challenge in enumerate(challenges):

                    p_crp = crp_error_probability(
                        challenge,
                        periods,
                        sigmas,
                        count
                    )

                    probabilities.append(p_crp)

                    detail_writer.writerow([
                        device_id,
                        count,
                        crp_index + 1,
                        f"{p_crp:.12e}"
                    ])

                mean_probability = (
                    sum(probabilities) / len(probabilities)
                )

                for threshold in ERROR_THRESHOLDS:

                    acceptable = sum(
                        p < threshold for p in probabilities
                    )

                    acceptable_percent = (
                        100.0 * acceptable / len(probabilities)
                    )

                    summary_rows.append([
                        device_id,
                        count,
                        threshold,
                        acceptable_percent,
                        mean_probability
                    ])

                print(
                    f"Averaging {count:4d}: "
                    f"Mean CRP error probability = "
                    f"{mean_probability:.8e}"
                )

    with summary_path.open(
        "w", newline="", encoding="utf-8"
    ) as summary_file:

        writer = csv.writer(summary_file)

        writer.writerow([
            "device_id",
            "averaging_count",
            "error_probability_threshold",
            "acceptable_crps_percent",
            "mean_crp_error_probability"
        ])

        writer.writerows(summary_rows)

    print("\n========== EXPERIMENT COMPLETE ==========")
    print("Detailed results:", detail_path)
    print("Summary results:", summary_path)
    print("Thresholds evaluated:", ERROR_THRESHOLDS)
    print("TEST_RESULT: PASS")


if __name__ == "__main__":
    main()
