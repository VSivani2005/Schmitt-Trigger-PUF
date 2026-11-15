"""Generate reproducible synthetic Schmitt-trigger thresholds."""

import random
import model_config as cfg

# Explicit synthetic assumptions; not measured FPGA specifications.
NOMINAL_VIH = 2.00
NOMINAL_VIL = 1.10

DEVICE_VARIATION_V = 0.025
PIN_VARIATION_V = 0.035


def generate_virtual_devices(config):
    rng = random.Random(config.RANDOM_SEED)
    devices = {}

    for device_id in range(config.NUM_DEVICES):
        device_vih_offset = rng.gauss(0, DEVICE_VARIATION_V)
        device_vil_offset = rng.gauss(0, DEVICE_VARIATION_V)

        pins = []

        for pin_id in range(config.NUM_PINS):
            vih = (
                NOMINAL_VIH
                + device_vih_offset
                + rng.gauss(0, PIN_VARIATION_V)
            )

            vil = (
                NOMINAL_VIL
                + device_vil_offset
                + rng.gauss(0, PIN_VARIATION_V)
            )

            # Keep generated values physically valid.
            vih = min(max(vih, 1.70), config.VDD_VOLTS - 0.20)
            vil = min(max(vil, 0.50), vih - 0.20)

            pins.append({
                "pin_id": pin_id,
                "vih": vih,
                "vil": vil
            })

        devices[device_id] = pins

    return devices


def validate_devices(devices, config):
    assert len(devices) == config.NUM_DEVICES

    for pins in devices.values():
        assert len(pins) == config.NUM_PINS

        for pin in pins:
            assert 0 < pin["vil"] < pin["vih"] < config.VDD_VOLTS

    return True


if __name__ == "__main__":
    virtual_devices = generate_virtual_devices(cfg)
    validate_devices(virtual_devices, cfg)

    print("========== VIRTUAL DEVICE GENERATION ==========")
    print("Devices:", len(virtual_devices))
    print("Pins per device:", cfg.NUM_PINS)

    for device_id, pins in virtual_devices.items():
        vih_values = [p["vih"] for p in pins]
        vil_values = [p["vil"] for p in pins]

        print(
            f"Device {device_id + 1}: "
            f"ViH range = {min(vih_values):.4f} to {max(vih_values):.4f} V, "
            f"ViL range = {min(vil_values):.4f} to {max(vil_values):.4f} V"
        )

    print("Threshold validation: PASS")
    print("TEST_RESULT: PASS")
