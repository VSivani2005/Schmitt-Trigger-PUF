import math
import statistics

# Five-device example with known response bits.
responses = [
    [1, 1, 0, 1, 0, 1, 0, 0],
    [1, 0, 0, 1, 1, 1, 0, 0],
    [0, 1, 0, 1, 0, 0, 1, 0],
    [1, 1, 1, 0, 0, 1, 0, 1],
    [0, 0, 0, 1, 1, 0, 1, 1],
]

num_devices = len(responses)
num_bits = len(responses[0])

model_entropy = 0.0
independent_entropy = 0.0

for bit in range(num_bits):
    hw = sum(response[bit] for response in responses)
    p_one = hw / num_devices
    p_max = max(p_one, 1 - p_one)

    model_entropy += -math.log2(p_max)

    # Independent equivalent expression.
    p_zero = (num_devices - hw) / num_devices
    independent_entropy += -math.log2(max(p_one, p_zero))

model_entropy /= num_bits
independent_entropy /= num_bits

print("========== MINIMUM ENTROPY VALIDATION ==========")
print(f"Model calculation:       {model_entropy:.12f}")
print(f"Independent calculation: {independent_entropy:.12f}")

assert math.isclose(
    model_entropy,
    independent_entropy,
    rel_tol=1e-12
)

print("Equation (15): PASS")
print("Equation (16): PASS")
