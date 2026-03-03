import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from kepler_core import *
from integrators import rk4_integrator

# -------------------------
# PARAMETERS
# -------------------------

dt = 0.00625
orbits = 100
total_time = orbits * ORBITAL_PERIOD

eccentricities = np.round(np.arange(0.1, 0.8, 0.1), 1)

base_path = "RK4_p"
orbit_path = os.path.join(base_path, "Orbit_PNGs")
energy_path = os.path.join(base_path, "Energy_PNGs")
data_path = os.path.join(base_path, "Data")

os.makedirs(orbit_path, exist_ok=True)
os.makedirs(energy_path, exist_ok=True)
os.makedirs(data_path, exist_ok=True)

results = []

# -------------------------
# MAIN LOOP
# -------------------------

for e in eccentricities:

    print(f"Running RK4 for e = {e}")

    r0, v0 = initial_conditions(e, "periapsis")

    r, v, t = rk4_integrator(r0, v0, dt, total_time)

    # Compute energy and angular momentum
    E = np.array([energy(r[i], v[i]) for i in range(len(t))])
    frac_error = np.abs((E - TRUE_ENERGY) / TRUE_ENERGY)

    L = np.array([angular_momentum(r[i], v[i]) for i in range(len(t))])

    final_error = frac_error[-1]
    energy_range = E.max() - E.min()
    L_dev = abs(L[-1] - L[0])

    # Save orbit plot
    plt.figure()
    plt.plot(r[:,0], r[:,1])
    plt.axis("equal")
    plt.title(f"RK4 Orbit e={e}")
    plt.savefig(os.path.join(orbit_path, f"orbit_e_{e:.1f}.png"))
    plt.close()

    # Save energy plot
    plt.figure()
    plt.plot(t, frac_error)
    plt.title(f"RK4 Fractional Energy Error e={e}")
    plt.savefig(os.path.join(energy_path, f"energy_e_{e:.1f}.png"))
    plt.close()

    # Save raw data
    np.save(os.path.join(data_path, f"r_e_{e:.1f}.npy"), r)
    np.save(os.path.join(data_path, f"v_e_{e:.1f}.npy"), v)
    np.save(os.path.join(data_path, f"t_e_{e:.1f}.npy"), t)

    results.append([
        e,
        dt,
        orbits,
        len(t),
        final_error,
        energy_range,
        L_dev
    ])

    del r, v, t, E, L

# -------------------------
# SAVE SUMMARY CSV
# -------------------------

df = pd.DataFrame(results, columns=[
    "eccentricity",
    "dt",
    "orbits",
    "steps",
    "final_fractional_energy_error",
    "energy_range",
    "angular_momentum_deviation"
])

df.to_csv(os.path.join(data_path, "rk4_summary.csv"), index=False)

print("All RK4 runs completed successfully.")