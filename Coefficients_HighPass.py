import scipy.signal as signal
import numpy as np

# --- Parameters ---
num_taps = 81
sample_rate = 48000
# Optimized Target: 1781 Hz (Yields actual ~2000 Hz)
target_cutoff = 1781

# --- Generate Coefficients ---
# pass_zero=False means High Pass
taps = signal.firwin(
    numtaps=num_taps, 
    cutoff=target_cutoff, 
    window=('kaiser', 4), 
    fs=sample_rate, 
    pass_zero=False 
)

# --- Print for Vivado ---
print("--- High Pass Coefficients ---")
print(','.join([f"{t:.18f}" for t in taps]))
