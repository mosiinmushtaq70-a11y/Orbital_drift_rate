import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("Verlet/Data/verlet_summary.csv")
df["eccentricity"] = df["eccentricity"].round(2)

# ----------------------------
# Log-Log Scaling (Amplitude, e ≤ 0.7)
# ----------------------------

mask = df["eccentricity"] <= 0.7

x = 1 - df["eccentricity"][mask]
y = df["energy_range"][mask]

plt.figure()
plt.loglog(x, y, marker='o')
plt.xlabel("1 - e")
plt.ylabel("Energy Oscillation Amplitude")
plt.title("Verlet (Pericenter) Log-Log Scaling (Amplitude, e ≤ 0.7)")
plt.grid(True, which="both")
plt.savefig("Verlet/loglog_amplitude.png")
plt.close()

coeffs = np.polyfit(np.log(x), np.log(y), 1)
slope = coeffs[0]
k_estimate = -slope

print("\nEstimated Verlet (Pericenter) amplitude scaling exponent k ≈", round(k_estimate, 4))