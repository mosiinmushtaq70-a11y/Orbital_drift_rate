"""
Generate the two Master Figures for the research paper.

Fig1: Master Convergence Overlay (log-log, 3 methods at pericenter)
Fig2: Start Location Effect (semi-log, RK4 at e=0.7, Peri vs Apo)
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from kepler_core import energy, TRUE_ENERGY, ORBITAL_PERIOD

# ============================================================
# Fig 1: Master Convergence Overlay
# ============================================================

df_euler = pd.read_csv("Euler_p/Data/euler_summary.csv")
df_rk4   = pd.read_csv("RK4_p/Data/rk4_summary.csv")
df_verlet = pd.read_csv("Verlet/Data/verlet_summary.csv")

for df in [df_euler, df_rk4, df_verlet]:
    df["eccentricity"] = df["eccentricity"].round(2)

fig1, ax1 = plt.subplots(figsize=(8, 6))

ax1.loglog(
    1 - df_euler["eccentricity"],
    df_euler["final_fractional_energy_error"],
    marker='o', linewidth=1.5, markersize=6,
    label="Euler (1st order)", color='#e74c3c'
)

ax1.loglog(
    1 - df_rk4["eccentricity"],
    df_rk4["final_fractional_energy_error"],
    marker='s', linewidth=1.5, markersize=6,
    label="RK4 (4th order)", color='#2980b9'
)

ax1.loglog(
    1 - df_verlet["eccentricity"],
    df_verlet["final_fractional_energy_error"],
    marker='^', linewidth=1.5, markersize=6,
    label="Velocity Verlet (symplectic)", color='#27ae60'
)

ax1.set_xlabel(r"$(1 - e)$", fontsize=13)
ax1.set_ylabel(r"Final Fractional Energy Error $|\Delta E / E_0|$", fontsize=13)
ax1.set_title("Master Convergence: Energy Drift vs Eccentricity (100 Orbits)", fontsize=14)
ax1.legend(fontsize=11, loc='upper right')
ax1.grid(True, which="both", alpha=0.4)
ax1.invert_xaxis()

fig1.tight_layout()
fig1.savefig("Fig1_Master_Convergence.png", dpi=200)
plt.close(fig1)

print("✓ Fig1_Master_Convergence.png saved.")

# ============================================================
# Fig 2: Start Location Effect — 1×3 subplot (e = 0.7)
#         Panel 1: Euler | Panel 2: RK4 | Panel 3: Verlet
# ============================================================

PERI_COLOR = '#e74c3c'
APO_COLOR  = '#2980b9'

def load_and_compute(method_peri_dir, method_apo_dir, e_str="0.7"):
    """Load .npy trajectory data and compute fractional energy error arrays."""
    data = {}
    for label, d in [("peri", method_peri_dir), ("apo", method_apo_dir)]:
        r = np.load(f"{d}/Data/r_e_{e_str}.npy")
        v = np.load(f"{d}/Data/v_e_{e_str}.npy")
        t = np.load(f"{d}/Data/t_e_{e_str}.npy")
        E = np.array([energy(r[i], v[i]) for i in range(len(t))])
        frac_err = np.abs((E - TRUE_ENERGY) / TRUE_ENERGY)
        orbits = t / ORBITAL_PERIOD
        data[label] = (orbits, frac_err)
        del r, v, t, E
    return data

# Load all three methods
euler_data  = load_and_compute("Euler_p", "Euler_Apo")
rk4_data    = load_and_compute("RK4_p",   "RK4_Apo")
verlet_data = load_and_compute("Verlet",   "Verlet_Apo")

fig2, axes = plt.subplots(1, 3, figsize=(18, 5.5), sharey=False)

# ── Panel 1: Euler ──
ax = axes[0]
ax.semilogy(euler_data["peri"][0], euler_data["peri"][1],
            linewidth=0.6, alpha=0.8, color=PERI_COLOR, label="Pericenter")
ax.semilogy(euler_data["apo"][0], euler_data["apo"][1],
            linewidth=0.6, alpha=0.8, color=APO_COLOR, label="Apocenter")
ax.set_title(r"Euler (1st order) — $e = 0.7$", fontsize=12, fontweight='bold')
ax.set_xlabel("Time (Orbits)", fontsize=11)
ax.set_ylabel(r"$|\Delta E / E_0|$", fontsize=12)
ax.legend(fontsize=9, loc='lower right')
ax.grid(True, which="both", alpha=0.3)
ax.set_xlim(0, 100)
ax.annotate("~11.7% baseline\ndivergence",
            xy=(0.55, 0.15), xycoords='axes fraction',
            fontsize=8.5, color='#555', fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fff3cd', edgecolor='#e0c36a', alpha=0.85))

# ── Panel 2: RK4 ──
ax = axes[1]
ax.semilogy(rk4_data["peri"][0], rk4_data["peri"][1],
            linewidth=0.6, alpha=0.8, color=PERI_COLOR, label="Pericenter")
ax.semilogy(rk4_data["apo"][0], rk4_data["apo"][1],
            linewidth=0.6, alpha=0.8, color=APO_COLOR, label="Apocenter")
ax.set_title(r"RK4 (4th order) — $e = 0.7$", fontsize=12, fontweight='bold')
ax.set_xlabel("Time (Orbits)", fontsize=11)
ax.legend(fontsize=9, loc='lower right')
ax.grid(True, which="both", alpha=0.3)
ax.set_xlim(0, 100)
ax.annotate("Lines overlap\nperfectly",
            xy=(0.55, 0.15), xycoords='axes fraction',
            fontsize=8.5, color='#555', fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#d4edda', edgecolor='#85c79b', alpha=0.85))

# ── Panel 3: Verlet ──
ax = axes[2]
ax.semilogy(verlet_data["peri"][0], verlet_data["peri"][1],
            linewidth=0.5, alpha=0.75, color=PERI_COLOR, label="Pericenter")
ax.semilogy(verlet_data["apo"][0], verlet_data["apo"][1],
            linewidth=0.5, alpha=0.75, color=APO_COLOR, label="Apocenter")
ax.set_title(r"Velocity Verlet (symplectic) — $e = 0.7$", fontsize=12, fontweight='bold')
ax.set_xlabel("Time (Orbits)", fontsize=11)
ax.legend(fontsize=9, loc='lower right')
ax.grid(True, which="both", alpha=0.3)
ax.set_xlim(0, 100)
ax.annotate("Oscillation bands\nsuperimposed",
            xy=(0.48, 0.15), xycoords='axes fraction',
            fontsize=8.5, color='#555', fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#d4edda', edgecolor='#85c79b', alpha=0.85))

fig2.suptitle("Start Location Effect: Pericenter vs. Apocenter at $e = 0.7$ (100 Orbits)",
              fontsize=14, fontweight='bold', y=1.01)
fig2.tight_layout()
fig2.savefig("Fig2_Start_Location_Effect.png", dpi=200, bbox_inches='tight')
plt.close(fig2)

print("✓ Fig2_Start_Location_Effect.png saved (3-panel).")
print("\nBoth master figures generated successfully.")

