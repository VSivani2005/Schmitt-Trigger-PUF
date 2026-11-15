import math
import sys

sys.path.insert(0, "src")

from error_probability_experiment import (
    bit_error_probability,
    crp_error_probability
)

# Equation (11): use a moderate separation/noise ratio.
mean_a = 25e-6
mean_b = 24.8e-6
sigma_a = 0.1e-6
sigma_b = 0.1e-6

z = abs(mean_a - mean_b) / math.sqrt(
    sigma_a**2 + sigma_b**2
)

expected_bit = 0.5 * math.erfc(z / math.sqrt(2))
actual_bit = bit_error_probability(
    mean_a, mean_b, sigma_a, sigma_b
)

# Equation (12): two independent bit-error events.
challenge = [(0, 1), (1, 2)]
periods = [25e-6, 24.8e-6, 24.6e-6]
sigmas = [0.1e-6, 0.1e-6, 0.1e-6]

p1 = bit_error_probability(
    periods[0], periods[1], sigmas[0], sigmas[1]
)
p2 = bit_error_probability(
    periods[1], periods[2], sigmas[1], sigmas[2]
)

# Stable independent calculation of 1 - (1-p1)(1-p2).
expected_crp = -math.expm1(
    math.log1p(-p1) + math.log1p(-p2)
)

actual_crp = crp_error_probability(
    challenge, periods, sigmas, 1
)

print("========== ERROR EQUATION VALIDATION ==========")
print(f"Bit probability 1:       {p1:.12e}")
print(f"Bit probability 2:       {p2:.12e}")
print(f"Equation (11) expected:  {expected_bit:.12e}")
print(f"Equation (11) model:     {actual_bit:.12e}")
print(f"Equation (12) expected:  {expected_crp:.12e}")
print(f"Equation (12) model:     {actual_crp:.12e}")

assert math.isclose(actual_bit, expected_bit, rel_tol=1e-12)
assert math.isclose(actual_crp, expected_crp, rel_tol=1e-12)

print("Equation (11): PASS")
print("Equation (12): PASS")
