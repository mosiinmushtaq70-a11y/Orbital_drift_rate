"""
validate_timestep_robustness.py
─────────────────────────────────
Sensitivity analysis: verify that the power-law scaling exponents (k)
are intrinsic to each integrator and not artifacts of the chosen Δt.

Compares k-values at two time steps:
  Baseline:   Δt₁ = 0.00625
  Validation:  Δt₂ = 0.003125  (half the baseline)

Output:
  - Console comparison table
  - timestep_robustness.csv
"""

import os
import numpy as np
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from kepler_core import initial_conditions, energy, TRUE_ENERGY, ORBITAL_PERIOD
from integrators import euler_integrator, rk4_integrator, verlet_integrator

# ── Configuration ──
ECCENTRICITIES = np.round(np.arange(0.1, 0.8, 0.1), 1)
ORBITS = 100
TOTAL_TIME = ORBITS * ORBITAL_PERIOD
DT_BASELINE = 0.00625
DT_FINE     = 0.003125   # half the baseline

METHODS = {
    "Euler":  euler_integrator,
    "RK4":   rk4_integrator,
    "Verlet": verlet_integrator,
}


def run_sweep(dt):
    """Run all methods across all eccentricities at a given dt.
    Returns dict: method_name -> array of final fractional energy errors."""
    results = {}
    for name, integrator in METHODS.items():
        errors = []
        for e in ECCENTRICITIES:
            r0, v0 = initial_conditions(e, "periapsis")
            r, v, t = integrator(r0, v0, dt, TOTAL_TIME)

            E = np.array([energy(r[i], v[i]) for i in range(len(t))])
            frac_err = np.abs((E - TRUE_ENERGY) / TRUE_ENERGY)

            if name == "Verlet":
                # Use oscillation amplitude (energy range) for symplectic method
                metric = E.max() - E.min()
            else:
                # Use final fractional energy error for non-symplectic methods
                metric = frac_err[-1]

            errors.append(metric)
            del r, v, t, E, frac_err

        results[name] = np.array(errors)
    return results


def extract_k(errors_array):
    """OLS regression on log(error) vs log(1-e) → returns (k, R²)."""
    x = np.log(1 - ECCENTRICITIES)
    y = np.log(errors_array)
    # Fit: y = slope * x + intercept
    coeffs = np.polyfit(x, y, 1)
    slope = coeffs[0]
    k = -slope

    # R² calculation
    y_pred = np.polyval(coeffs, x)
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - ss_res / ss_tot

    return k, r_squared


# ════════════════════════════════════════════
# Main execution
# ════════════════════════════════════════════
if __name__ == "__main__":

    print("=" * 65)
    print("  TIME-STEP ROBUSTNESS VALIDATION")
    print(f"  Baseline Δt = {DT_BASELINE}  |  Fine Δt = {DT_FINE}")
    print(f"  Orbits = {ORBITS}  |  e ∈ [{ECCENTRICITIES[0]}, {ECCENTRICITIES[-1]}]")
    print("=" * 65)

    # ── Run baseline sweep ──
    print(f"\n▶ Running baseline sweep (Δt = {DT_BASELINE})...")
    results_baseline = run_sweep(DT_BASELINE)
    print("  ✓ Baseline complete.")

    # ── Run fine sweep ──
    print(f"\n▶ Running fine sweep (Δt = {DT_FINE})...")
    results_fine = run_sweep(DT_FINE)
    print("  ✓ Fine sweep complete.")

    # ── Extract k-values and build comparison ──
    rows = []
    print("\n" + "=" * 65)
    print(f"  {'Method':<10} {'k (baseline)':>13} {'k (fine)':>13} {'Δk (%)':>10} {'R²(base)':>10} {'R²(fine)':>10}")
    print("-" * 65)

    for name in METHODS:
        k_base, r2_base = extract_k(results_baseline[name])
        k_fine, r2_fine = extract_k(results_fine[name])
        pct_diff = abs(k_fine - k_base) / k_base * 100

        print(f"  {name:<10} {k_base:>13.4f} {k_fine:>13.4f} {pct_diff:>9.2f}% {r2_base:>10.6f} {r2_fine:>10.6f}")

        rows.append({
            "method": name,
            "k_baseline": round(k_base, 4),
            "k_fine": round(k_fine, 4),
            "pct_difference": round(pct_diff, 2),
            "R2_baseline": round(r2_base, 6),
            "R2_fine": round(r2_fine, 6),
        })

    print("=" * 65)

    # ── Verdict ──
    max_diff = max(r["pct_difference"] for r in rows)
    if max_diff < 5.0:
        print(f"\n✅ ROBUST: Maximum k-shift is {max_diff:.2f}% (< 5% threshold).")
        print("   The scaling exponents are intrinsic to the integrators.")
    else:
        print(f"\n⚠️  WARNING: Maximum k-shift is {max_diff:.2f}% (≥ 5% threshold).")
        print("   Further investigation may be needed.")

    # ── Save raw data ──
    # Per-eccentricity errors for both time steps
    detail_rows = []
    for name in METHODS:
        for i, e in enumerate(ECCENTRICITIES):
            detail_rows.append({
                "method": name,
                "eccentricity": e,
                "error_baseline": results_baseline[name][i],
                "error_fine": results_fine[name][i],
            })

    df_summary = pd.DataFrame(rows)
    df_detail  = pd.DataFrame(detail_rows)

    df_summary.to_csv("timestep_robustness_summary.csv", index=False)
    df_detail.to_csv("timestep_robustness_detail.csv", index=False)

    print(f"\n✓ Saved: timestep_robustness_summary.csv")
    print(f"✓ Saved: timestep_robustness_detail.csv")
    print("\nDone.")
