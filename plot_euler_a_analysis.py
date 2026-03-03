import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# Load Euler Apo Data
# ----------------------------

df = pd.read_csv("Euler_Apo/Data/euler_apo_summary.csv")
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
plt.title("Euler (Apoapsis) Log-Log Scaling (e ≤ 0.7)")
plt.grid(True, which="both")
plt.savefig("Euler_Apo/loglog_scaling.png")
plt.close()

# ----------------------------
# Estimate exponent
# ----------------------------

coeffs = np.polyfit(np.log(x), np.log(y), 1)
slope = coeffs[0]
k_estimate = -slope

print("\nEstimated Euler (Apoapsis) power-law exponent k ≈", round(k_estimate, 4))
print("Scaling roughly: error ∝ (1 - e)^(-k)")