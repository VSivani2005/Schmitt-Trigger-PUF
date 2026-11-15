"""RC oscillator model based on Equation (5) of the reference paper."""

import math

def oscillator_period(vih, vil, vdd, resistance, capacitance):
    """
    Calculate the Schmitt-trigger oscillator period in seconds.

    P = RC * ln((ViH * (VDD - ViL)) /
                (ViL * (VDD - ViH)))
    """

    if not (0 < vil < vih < vdd):
        raise ValueError(
            "Thresholds must satisfy 0 < ViL < ViH < VDD"
        )

    if resistance <= 0 or capacitance <= 0:
        raise ValueError("R and C must be positive")

    ratio = (vih * (vdd - vil)) / (vil * (vdd - vih))

    return resistance * capacitance * math.log(ratio)


def period_to_counter_cycles(period_seconds, clock_hz):
    """Convert oscillator period into ideal FPGA counter cycles."""

    if period_seconds <= 0 or clock_hz <= 0:
        raise ValueError("Period and clock frequency must be positive")

    return round(period_seconds * clock_hz)


def period_to_frequency(period_seconds):
    """Convert period in seconds to frequency in Hz."""

    if period_seconds <= 0:
        raise ValueError("Period must be positive")

    return 1.0 / period_seconds


def calculate_pin_period(vih, vil, config):
    """Calculate period and equivalent FPGA counter measurement."""

    period = oscillator_period(
        vih,
        vil,
        config.VDD_VOLTS,
        config.RESISTANCE_OHMS,
        config.CAPACITANCE_FARADS
    )

    cycles = period_to_counter_cycles(
        period,
        config.COUNTER_CLOCK_HZ
    )

    return {
        "period_seconds": period,
        "period_microseconds": period * 1e6,
        "frequency_hz": period_to_frequency(period),
        "counter_cycles": cycles
    }
