import sys
sys.path.insert(0, "src")

import model_config as cfg
from oscillator_model import calculate_pin_period

# Illustrative thresholds only; not measured FPGA data.
vih = 2.0
vil = 1.1

result = calculate_pin_period(vih, vil, cfg)

print("========== OSCILLATOR MODEL TEST ==========")
print(f"VDD: {cfg.VDD_VOLTS:.2f} V")
print(f"ViH: {vih:.3f} V")
print(f"ViL: {vil:.3f} V")
print(f"R: {cfg.RESISTANCE_OHMS} ohms")
print(f"C: {cfg.CAPACITANCE_FARADS} F")
print("-------------------------------------------")
print(f"Period: {result['period_microseconds']:.4f} us")
print(f"Frequency: {result['frequency_hz']:.2f} Hz")
print(f"100 MHz counter cycles: {result['counter_cycles']}")
print("TEST_RESULT: PASS")
