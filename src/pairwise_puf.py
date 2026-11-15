"""Generate a 128-bit pairwise PUF response for each virtual device."""

import random
import sys
import csv
from pathlib import Path

sys.path.insert(0, "src")

import model_config as cfg
from threshold_model import generate_virtual_devices
from oscillator_model import calculate_pin_period


def calculate_device_counts(devices):
    """Return 100 MHz counter counts for each device's 30 pins."""
    all_counts = {}

    for device_id, pins in devices.items():
        counts = []

        for pin in pins:
            result = calculate_pin_period(
                pin["vih"], pin["vil"], cfg
            )
            counts.append(result["counter_cycles"])

        all_counts[device_id] = counts

    return all_counts


def generate_challenge(num_bits, num_pins, seed):
    """Generate distinct-pin pairs encoded as 10-bit challenge words."""
    rng = random.Random(seed)
    challenge = []

    for _ in range(num_bits):
        first, second = rng.sample(range(num_pins), 2)
        word = (first << 5) | second
        challenge.append((first, second, word))

    return challenge


def generate_responses(device_counts, challenge):
    responses = {}

    for device_id, counts in device_counts.items():
        bits = []

        for first, second, _word in challenge:
            bits.append("1" if counts[first] > counts[second] else "0")

        responses[device_id] = "".join(bits)

    return responses


if __name__ == "__main__":
    devices = generate_virtual_devices(cfg)
    device_counts = calculate_device_counts(devices)

    challenge = generate_challenge(
        cfg.RESPONSE_BITS,
        cfg.NUM_PINS,
        cfg.RANDOM_SEED + 1
    )

    responses = generate_responses(device_counts, challenge)

    assert len(challenge) == cfg.RESPONSE_BITS
    assert all(len(response) == cfg.RESPONSE_BITS
               for response in responses.values())
    assert all(first != second for first, second, _ in challenge)
    assert all(0 <= word < 1024 for _, _, word in challenge)

    output_path = Path("results") / "pairwise_responses.csv"

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["device_id", "response_bits", "response_length"])

        for device_id, response in responses.items():
            writer.writerow([
                device_id + 1,
                response,
                len(response)
            ])

    print("========== PAIRWISE PUF RESPONSE TEST ==========")
    print("Challenge words:", len(challenge))
    print("Bits per challenge word: 10")
    print("Response length:", cfg.RESPONSE_BITS)

    print("\nFirst 5 challenge words:")
    for first, second, word in challenge[:5]:
        print(
            f"Pins ({first:02d}, {second:02d}) "
            f"-> {word:010b}"
        )

    print("\nDevice responses:")
    for device_id, response in responses.items():
        print(
            f"Device {device_id + 1}: {response} "
            f"({len(response)} bits)"
        )

    print("\nCSV saved to:", output_path)
    print("TEST_RESULT: PASS")
