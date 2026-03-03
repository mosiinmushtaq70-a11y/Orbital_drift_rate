import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------
# Ensure RK4 folder exists
# ----------------------------
os.makedirs("RK4_p", exist_ok=True)

# ----------------------------
# Load RK4 Data
# ----------------------------

df = pd.read_csv("RK4_p/Data/rk4_summary.csv")
df["eccentricity"] = df["eccentricity"].round(2)

# ----------------------------
# Log-Log Scaling (e ≤ 0.7)
# ----------------------------

mask = df["eccentricity"] <= 0.7

x = 1 - df["eccentricity"][mask]
y = df["final_fractional_energy_error"][mask]

plt.figure()
plt.loglog(x, y, marker='o')
plt.xlabel("1 - e")
plt.ylabel("Final Fractional Energy Error")
plt.title("RK4 (Pericenter) Log-Log Scaling (e ≤ 0.7)")
plt.grid(True, which="both")
plt.savefig("RK4_p/loglog_scaling.png")
plt.close()

# ----------------------------
# Estimate exponent
# ----------------------------

coeffs = np.polyfit(np.log(x), np.log(y), 1)
slope = coeffs[0]
k_estimate = -slope

print("\nEstimated RK4 (Pericenter) power-law exponent k ≈", round(k_estimate, 4))
print("Scaling roughly: error ∝ (1 - e)^(-k)")