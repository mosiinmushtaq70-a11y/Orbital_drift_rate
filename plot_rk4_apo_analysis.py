import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load RK4 Apo data
df = pd.read_csv("RK4_Apo/Data/rk4_apo_summary.csv")
df["eccentricity"] = df["eccentricity"].round(2)

one_minus_e = 1 - df["eccentricity"]

# Log-log scaling (e ≤ 0.7)
mask = df["eccentricity"] <= 0.7

x = one_minus_e[mask]
y = df["final_fractional_energy_error"][mask]

plt.figure()
plt.loglog(x, y, marker='o')
plt.xlabel("1 - e")
plt.ylabel("Final Fractional Energy Error")
plt.title("RK4 (Apoapsis) Log-Log Scaling (e ≤ 0.7)")
plt.grid(True, which="both")
plt.savefig("RK4_Apo/loglog_scaling.png")
plt.close()

coeffs = np.polyfit(np.log(x), np.log(y), 1)
k_estimate = -coeffs[0]

print("\nRK4 (Apoapsis) exponent k ≈", round(k_estimate, 4))