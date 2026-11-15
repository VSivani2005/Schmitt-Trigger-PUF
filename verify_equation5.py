import math
import sys

sys.path.insert(0, "src")

import model_config as cfg
from oscillator_model import oscillator_period, calculate_pin_period

vih = 2.00
vil = 1.10

expected = (
    cfg.RESISTANCE_OHMS
    * cfg.CAPACITANCE_FARADS
    * math.log(
        (vih * (cfg.VDD_VOLTS - vil))
        / (vil * (cfg.VDD_VOLTS - vih))
    )
)

actual = oscillator_period(
    vih,
    vil,
    cfg.VDD_VOLTS,
    cfg.RESISTANCE_OHMS,
    cfg.CAPACITANCE_FARADS
)

result = calculate_pin_period(vih, vil, cfg)

print("========== EQUATION (5) VALIDATION ==========")
print(f"Independent calculation: {expected * 1e6:.6f} us")
print(f"Model calculation:       {actual * 1e6:.6f} us")
print(f"Frequency:               {result['frequency_hz']:.2f} Hz")
print(f"Counter cycles:          {result['counter_cycles']}")

assert math.isclose(actual, expected, rel_tol=1e-12)
assert result["counter_cycles"] == round(expected * cfg.COUNTER_CLOCK_HZ)

print("Equation (5): PASS")
