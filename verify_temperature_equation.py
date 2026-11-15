import math
import sys

sys.path.insert(0, "src")

import model_config as cfg

# Test values
period_25 = 25e-6
span = 0.005

t_ref = cfg.REFERENCE_TEMPERATURE_C
t_max = max(cfg.TEMPERATURES_C)

lam = (
    period_25 * span
    / (t_max**1.6 - t_ref**1.6)
)

mu = period_25 - lam * t_ref**1.6

def model_period(t):
    return lam * t**1.6 + mu

expected_25 = period_25
expected_65 = period_25 * (1 + span)

actual_25 = model_period(25)
actual_65 = model_period(65)

print("========== EQUATION (14) VALIDATION ==========")
print(f"Lambda:             {lam:.12e}")
print(f"Mu:                 {mu:.12e}")
print(f"Period at 25 C:     {actual_25 * 1e6:.9f} us")
print(f"Expected at 25 C:   {expected_25 * 1e6:.9f} us")
print(f"Period at 65 C:     {actual_65 * 1e6:.9f} us")
print(f"Expected at 65 C:   {expected_65 * 1e6:.9f} us")

assert math.isclose(actual_25, expected_25, rel_tol=1e-12)
assert math.isclose(actual_65, expected_65, rel_tol=1e-12)

print("Equation (14): PASS")
