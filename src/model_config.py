"""
Paper configuration for the Schmitt-trigger PUF software model.

Reference:
Grossi et al., Novel PUF Implementation for
Microcontrollers and Field Programmable Gate Arrays.
"""

# Experimental architecture
NUM_DEVICES = 5
NUM_PINS = 30
RESPONSE_BITS = 128
NUM_CRPS = 10_000

# RC oscillator
RESISTANCE_OHMS = 22_000
CAPACITANCE_FARADS = 1e-9
VDD_VOLTS = 3.3

# FPGA period measurement
COUNTER_CLOCK_HZ = 100_000_000

# Period averaging experiments
AVERAGING_COUNTS = [1, 10, 50, 100, 500, 1000]

# Temperature reliability experiment
TEMPERATURES_C = [5, 15, 25, 35, 45, 55, 65]
REFERENCE_TEMPERATURE_C = 25

# Reproducibility
RANDOM_SEED = 20261115

# Explicitly synthetic model assumptions.
# These are NOT measured Artix-7 threshold values.
SYNTHETIC_MODEL = True
