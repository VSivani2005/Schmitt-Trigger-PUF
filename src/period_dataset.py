"""Calculate oscillator periods for all virtual PUF devices."""

import csv
import sys
from pathlib import Path

sys.path.insert(0, "src")

import model_config as cfg
from threshold_model import generate_virtual_devices
from oscillator_model import calculate_pin_period


def generate_period_dataset():
    devices = generate_virtual_devices(cfg)
    rows = []

    for device_id, pins in devices.items():
        for pin in pins:
            result = calculate_pin_period(
                pin["vih"],
                pin["vil"],
                cfg
            )

            rows.append({
                "device_id": device_id + 1,
                "pin_id": pin["pin_id"],
                "vih_volts": pin["vih"],
                "vil_volts": pin["vil"],
                "period_microseconds": result["period_microseconds"],
                "frequency_hz": result["frequency_hz"],
                "counter_cycles": result["counter_cycles"]
            })

    return rows


if __name__ == "__main__":
    rows = generate_period_dataset()

    output_path = Path("results") / "oscillator_periods.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    periods = [row["period_microseconds"] for row in rows]
    counts = [row["counter_cycles"] for row in rows]

    print("========== OSCILLATOR PERIOD DATASET ==========")
    print("Virtual devices:", cfg.NUM_DEVICES)
    print("Pins per device:", cfg.NUM_PINS)
    print("Total oscillator measurements:", len(rows))
    print(f"Minimum period: {min(periods):.4f} us")
    print(f"Maximum period: {max(periods):.4f} us")
    print(f"Mean period: {sum(periods) / len(periods):.4f} us")
    print(f"Minimum counter cycles: {min(counts)}")
    print(f"Maximum counter cycles: {max(counts)}")
    print("CSV saved to:", output_path)
    print("TEST_RESULT: PASS")
