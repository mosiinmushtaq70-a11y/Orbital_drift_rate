import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load Verlet Apo data
df = pd.read_csv("Verlet_Apo/Data/verlet_apo_summary.csv")
df["eccentricity"] = df["eccentricity"].round(2)

one_minus_e = 1 - df["eccentricity"]

# Use energy_range (oscillation amplitude), e ≤ 0.7
mask = df["eccentricity"] <= 0.7

x = one_minus_e[mask]
y = df["energy_range"][mask]

plt.figure()
plt.loglog(x, y, marker='o')
plt.xlabel("1 - e")
plt.ylabel("Energy Oscillation Amplitude")
plt.title("Verlet (Apoapsis) Log-Log Scaling (Amplitude, e ≤ 0.7)")
plt.grid(True, which="both")
plt.savefig("Verlet_Apo/loglog_amplitude.png")
plt.close()

coeffs = np.polyfit(np.log(x), np.log(y), 1)
k_estimate = -coeffs[0]

print("\nVerlet (Apoapsis) amplitude exponent k ≈", round(k_estimate, 4))