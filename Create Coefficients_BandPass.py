import scipy.signal as signal
import numpy as np

# --- Parameters ---
num_taps = 81
sample_rate = 48000
# Optimized Targets for [400, 2000]
compensated_targets = [219, 2224] 

# --- Generate Coefficients ---
# pass_zero=False means Band Pass
taps = signal.firwin(
    numtaps=num_taps, 
    cutoff=compensated_targets, 
    window=('kaiser', 4), 
    fs=sample_rate, 
    pass_zero=False 
)

# --- Print for Vivado ---
print("--- Band Pass Coefficients ---")
print(','.join([f"{t:.18f}" for t in taps]))
