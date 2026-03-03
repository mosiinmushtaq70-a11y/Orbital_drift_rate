import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from kepler_core import *
from integrators import verlet_integrator

dt = 0.00625
orbits = 100
total_time = orbits * ORBITAL_PERIOD

eccentricities = np.round(np.arange(0.1, 0.8, 0.1), 1)

base_path = "Verlet"
orbit_path = os.path.join(base_path, "Orbit_PNGs")
energy_path = os.path.join(base_path, "Energy_PNGs")
data_path = os.path.join(base_path, "Data")

os.makedirs(orbit_path, exist_ok=True)
os.makedirs(energy_path, exist_ok=True)
os.makedirs(data_path, exist_ok=True)

results = []

for e in eccentricities:

    print(f"Running Verlet for e = {e}")

    r0, v0 = initial_conditions(e, "periapsis")

    r, v, t = verlet_integrator(r0, v0, dt, total_time)

    E = np.array([energy(r[i], v[i]) for i in range(len(t))])
    frac_error = np.abs((E - TRUE_ENERGY) / TRUE_ENERGY)
    L = np.array([angular_momentum(r[i], v[i]) for i in range(len(t))])

    # Use max error over the last orbit to avoid phase-coincidence artifacts
    steps_per_orbit = int(round((2 * np.pi) / dt))
    final_error = frac_error[-steps_per_orbit:].max()
    energy_range = E.max() - E.min()
    L_dev = abs(L[-1] - L[0])

    plt.figure()
    plt.plot(r[:,0], r[:,1])
    plt.axis("equal")
    plt.title(f"Verlet Orbit e={e}")
    plt.savefig(os.path.join(orbit_path, f"orbit_e_{e:.1f}.png"))
    plt.close()

    plt.figure()
    plt.plot(t, frac_error)
    plt.title(f"Verlet Fractional Energy Error e={e}")
    plt.savefig(os.path.join(energy_path, f"energy_e_{e:.1f}.png"))
    plt.close()

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

df = pd.DataFrame(results, columns=[
    "eccentricity",
    "dt",
    "orbits",
    "steps",
    "final_fractional_energy_error",
    "energy_range",
    "angular_momentum_deviation"
])

df.to_csv(os.path.join(data_path, "verlet_summary.csv"), index=False)

print("All Verlet runs completed successfully.")