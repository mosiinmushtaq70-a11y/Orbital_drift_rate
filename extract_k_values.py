"""
Extract k-values (power-law exponents) from all 6 configurations
and save them into a single k_values_summary.csv ledger.
"""
import pandas as pd
import numpy as np

# ------------------------------------------
# Configuration: method, start, CSV path, metric
# ------------------------------------------
configs = [
    ("Euler",  "Pericenter", "Euler_p/Data/euler_summary.csv",       "final_fractional_energy_error"),
    ("Euler",  "Apocenter",  "Euler_Apo/Data/euler_apo_summary.csv", "final_fractional_energy_error"),
    ("RK4",    "Pericenter", "RK4_p/Data/rk4_summary.csv",           "final_fractional_energy_error"),
    ("RK4",    "Apocenter",  "RK4_Apo/Data/rk4_apo_summary.csv",     "final_fractional_energy_error"),
    ("Verlet", "Pericenter", "Verlet/Data/verlet_summary.csv",        "energy_range"),
    ("Verlet", "Apocenter",  "Verlet_Apo/Data/verlet_apo_summary.csv","energy_range"),
]

results = []

for method, start, csv_path, metric in configs:
    df = pd.read_csv(csv_path)
    df["eccentricity"] = df["eccentricity"].round(2)

    mask = df["eccentricity"] <= 0.7
    x = 1 - df["eccentricity"][mask]
    y = df[metric][mask]

    coeffs = np.polyfit(np.log(x.values), np.log(y.values), 1)
    slope = coeffs[0]
    k_value = -slope

    results.append({
        "method": method,
        "start_location": start,
        "metric": metric,
        "k_exponent": round(k_value, 4),
        "slope": round(slope, 4),
    })

    print(f"{method} ({start}): k = {k_value:.4f}  (slope = {slope:.4f})")

# Save to CSV
df_out = pd.DataFrame(results)
df_out.to_csv("k_values_summary.csv", index=False)

print("\n✓ k_values_summary.csv saved successfully.")
