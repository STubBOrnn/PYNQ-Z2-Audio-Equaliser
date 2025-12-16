import scipy.signal as signal
import numpy as np

# --- Parameters ---
num_taps = 81
sample_rate = 48000
# Optimized Target: 392 Hz (Yields actual ~400 Hz)
target_cutoff = 392 

# --- Generate Coefficients ---
# pass_zero=True means Low Pass
taps = signal.firwin(
    numtaps=num_taps, 
    cutoff=target_cutoff, 
    window=('kaiser', 4), 
    fs=sample_rate, 
    pass_zero=True 
)

# --- Print for Vivado ---
print("--- Low Pass Coefficients ---")
print(','.join([f"{t:.18f}" for t in taps]))
