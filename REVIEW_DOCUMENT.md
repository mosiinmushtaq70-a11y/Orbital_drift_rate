# Empirical Analysis of Eccentricity-Driven Secular Energy Drift in Numerical Integrators for the Kepler Two-Body Problem

---

## 1. Abstract

The secular growth of energy error in numerical integration of the unperturbed Kepler two-body problem was investigated as a function of orbital eccentricity $e$. Three integration schemes — the Forward Euler method (1st order), the Classical Runge-Kutta method (RK4, 4th order), and the Velocity Verlet method (2nd order, symplectic) — were applied to 100-orbit simulations across $e \in [0.1, 0.7]$ under natural units ($\mu = 1$, $a = 1$, $T = 2\pi$) with strict 64-bit floating-point arithmetic. The fractional energy error was found to obey a power-law scaling of the form $|\Delta E / E_0| \propto (1 - e)^{-k}$, with the exponent $k$ serving as a quantitative fingerprint of eccentricity sensitivity. The following exponents were measured: $k \approx 8.61$ for RK4, $k \approx 0.44$ for Euler, and $k \approx 4.88$ for the Verlet oscillation amplitude. The Velocity Verlet integrator exhibited bounded oscillatory energy error with zero secular drift, confirming its symplectic character. A secondary investigation into the effect of orbital starting location (periapsis vs. apoapsis) revealed that the first-order Euler method exhibits a ~25% sensitivity in its scaling exponent to initialization phase, whereas the higher-order RK4 and the symplectic Verlet methods are effectively invariant ($\Delta k < 0.001$).

---

## 2. Experimental Methodology

### 2.1 Governing Equations

The dynamics of the unperturbed Kepler two-body problem are governed by the Newtonian inverse-square gravitational acceleration:

$$\ddot{\mathbf{r}} = -\frac{\mu}{r^3}\,\mathbf{r}$$

where $\mathbf{r} \in \mathbb{R}^2$ is the position vector of the orbiting body relative to the central mass, $r = |\mathbf{r}|$ is the orbital radius, and $\mu = GM$ is the standard gravitational parameter.

The specific mechanical energy, a conserved quantity of the exact solution, is given by:

$$E = \frac{1}{2}\,|\dot{\mathbf{r}}|^2 - \frac{\mu}{r}$$

For a bound Keplerian orbit with semi-major axis $a$, the analytical energy is $E_0 = -\mu / 2a$. The diagnostic quantity used throughout this study is the fractional energy error:

$$\epsilon_E = \left| \frac{\Delta E}{E_0} \right| = \left| \frac{E(t) - E_0}{E_0} \right|$$

The angular momentum (a second conserved quantity of the planar Kepler problem) is defined as:

$$L_z = x\,\dot{y} - y\,\dot{x}$$

### 2.2 Normalization and Units

All simulations were conducted in a normalized unit system chosen to eliminate dimensional constants from the numerical computation:

| Quantity | Symbol | Value |
|---|---|---|
| Gravitational parameter | $\mu = GM$ | $1.0$ |
| Semi-major axis | $a$ | $1.0$ |
| Analytical energy | $E_0 = -\mu/2a$ | $-0.5$ |
| Orbital period | $T = 2\pi\sqrt{a^3/\mu}$ | $2\pi$ |

Initial conditions were derived from the vis-viva equation $v^2 = \mu(2/r - 1/a)$:

- **Periapsis start**: $r_0 = a(1 - e)$, $\quad v_0 = \sqrt{(1 + e)/(1 - e)}$
- **Apoapsis start**: $r_0 = a(1 + e)$, $\quad v_0 = \sqrt{(1 - e)/(1 + e)}$

### 2.3 Numerical Parameters

A fixed time step of $\Delta t = 0.00625$ was employed, yielding approximately 1,005 integration steps per orbit. Each simulation was evolved for $N_{\text{orb}} = 100$ complete orbits ($t_{\text{final}} = 200\pi$). The eccentricity domain was sampled at $e \in \{0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7\}$.

### 2.4 Critical Role of 64-bit Precision

An initial data campaign conducted under 32-bit single-precision arithmetic (`float32`, $\epsilon_{\text{mach}} \approx 1.2 \times 10^{-7}$) revealed that the RK4 fractional energy errors at moderate eccentricities ($e \leq 0.7$) were indistinguishable from the floating-point noise floor. All error values clustered around $\sim 10^{-5}$–$10^{-7}$ regardless of eccentricity, producing a spuriously flat $k$-value that reflected storage-precision limitations rather than algorithmic truncation error.

Upon upgrading to 64-bit double-precision arithmetic (`float64`, $\epsilon_{\text{mach}} \approx 2.2 \times 10^{-16}$), the RK4 errors at $e = 0.1$ dropped to $\sim 2.3 \times 10^{-10}$ — approximately **three orders of magnitude below** the former noise floor. This resolution was essential for isolating the true algorithmic truncation error from numerical round-off and for recovering the genuine power-law scaling of the RK4 integrator against eccentricity.

The precision upgrade also corrected a qualitative false positive in the start-location analysis (Section 5). Under 32-bit arithmetic, stochastic round-off noise compressed the RK4 errors into a narrow band between $10^{-7}$ and $10^{-5}$, within which random fluctuations masqueraded as a systematic baseline shift between pericenter and apocenter initializations. Under 64-bit precision, this artifact was eradicated: the RK4 and Velocity Verlet scaling exponents were found to be identical between start locations to within $0.02\%$, demonstrating that the start-location phase shock is a real physical phenomenon exclusive to first-order methods, not a general integrator property. All results reported herein were obtained under strict `float64` arithmetic throughout the entire computational pipeline, including initial conditions, integration arrays, and energy evaluation.

### 2.5 Integrator Descriptions

**Forward Euler** (1st-order explicit):

$$\mathbf{r}_{n+1} = \mathbf{r}_n + \mathbf{v}_n\,\Delta t, \qquad \mathbf{v}_{n+1} = \mathbf{v}_n + \mathbf{a}_n\,\Delta t$$

**Classical Runge-Kutta (RK4)** (4th-order explicit): The standard four-stage scheme applied to the coupled $(\mathbf{r}, \mathbf{v})$ system with stages evaluated at intermediate positions and velocities.

**Velocity Verlet** (2nd-order symplectic):

$$\mathbf{r}_{n+1} = \mathbf{r}_n + \mathbf{v}_n\,\Delta t + \tfrac{1}{2}\,\mathbf{a}_n\,\Delta t^2$$

$$\mathbf{v}_{n+1} = \mathbf{v}_n + \tfrac{1}{2}\,(\mathbf{a}_n + \mathbf{a}_{n+1})\,\Delta t$$

The Velocity Verlet method is a symplectic integrator: it exactly preserves the symplectic 2-form of the Hamiltonian phase space, implying that it integrates a nearby *shadow Hamiltonian* $\tilde{H} = H + \mathcal{O}(\Delta t^2)$. This guarantees bounded energy oscillations without secular drift over arbitrarily long integration times.

---

## 3. The Secular Drift Dichotomy

The central qualitative result of this study is the stark dichotomy between the energy error behavior of the explicit (non-symplectic) integrators and the symplectic Velocity Verlet scheme.

### 3.1 Explicit Integrators: Monotonic Secular Drift

Both the Forward Euler and RK4 methods produced energy errors that grew monotonically with time, exhibiting a clear secular drift. Over 100 orbits, the Euler method accumulated fractional energy errors reaching $\epsilon_E \sim 1.07$ at $e = 0.7$ — a complete failure in energy conservation where the numerical energy has drifted by more than 100% from the analytical value. The RK4 method, by virtue of its higher order, produced far smaller absolute errors ($\epsilon_E \sim 2.59 \times 10^{-6}$ at $e = 0.7$), but the error nonetheless grew monotonically without bound.

### 3.2 Symplectic Integrator: Bounded Oscillation

The Velocity Verlet method produced energy errors that oscillated quasi-periodically about the analytical value with **zero net secular drift**. At $e = 0.7$, the oscillation amplitude (energy range) was $\sim 5.06 \times 10^{-4}$, while the final instantaneous error was $\sim 9.70 \times 10^{-4}$. Crucially, the angular momentum deviation for Verlet remained at machine epsilon ($\sim 10^{-15}$–$10^{-16}$) across all eccentricities, confirming exact preservation of this integral of motion to within round-off.

For the Verlet integrator, the appropriate diagnostic quantity is therefore not the final instantaneous error (which samples the oscillation at an arbitrary phase) but rather the **oscillation amplitude** — the peak-to-peak energy range over the full simulation. This amplitude is the physically meaningful measure of how well the shadow Hamiltonian approximates the true Hamiltonian.

---

## 4. Power-Law Scaling Against Eccentricity

### 4.1 The Scaling Ansatz

As eccentricity increases, the orbital velocity at periapsis grows as $v_p = \sqrt{(1+e)/(1-e)}$, and the pericentric distance shrinks as $r_p = a(1-e)$. Both effects concentrate the gravitational dynamics into an increasingly narrow arc of the orbit, demanding higher temporal resolution. The resulting growth in truncation error is modeled by a power-law ansatz:

$$\epsilon_E \propto (1 - e)^{-k}$$

where $k > 0$ is the eccentricity scaling exponent. On a log-log plot of $\epsilon_E$ versus $(1 - e)$, this relationship manifests as a straight line with slope $-k$.

### 4.2 Master Convergence Overlay

![Fig. 1: Master Convergence — Log-log overlay of final fractional energy error vs. (1 − e) for Euler, RK4, and Velocity Verlet at pericenter start. The three methods span over 9 orders of magnitude in error.](C:/Users/Mosin/.gemini/antigravity/brain/e06af17c-2f24-4eeb-a03d-3200fdd30cc7/Fig1_Master_Convergence.png)

### 4.3 Measured Exponents

The power-law exponent $k$ was extracted via linear regression on $\ln(\epsilon_E)$ versus $\ln(1-e)$ over the domain $e \in [0.1, 0.7]$:

| Method | Start Location | Metric | $k$-Exponent | Slope |
|---|---|---|---|---|
| **Euler** | Pericenter | $\epsilon_E$ (final) | $0.4435$ | $-0.4435$ |
| **Euler** | Apocenter | $\epsilon_E$ (final) | $0.3540$ | $-0.3540$ |
| **RK4** | Pericenter | $\epsilon_E$ (final) | $8.6051$ | $-8.6051$ |
| **RK4** | Apocenter | $\epsilon_E$ (final) | $8.6053$ | $-8.6053$ |
| **Verlet** | Pericenter | Oscillation amplitude | $4.8797$ | $-4.8797$ |
| **Verlet** | Apocenter | Oscillation amplitude | $4.8789$ | $-4.8789$ |

### 4.4 Interpretation

The measured exponents reveal a hierarchy of eccentricity sensitivity that is strongly correlated with integrator order:

**Euler ($k \approx 0.44$):** The weak eccentricity dependence is consistent with the interpretation that the first-order Euler method's global truncation error ($\mathcal{O}(\Delta t)$) is dominated by the accumulation of local errors proportional to the step size, with only a mild amplification at periapsis. The error at $e = 0.7$ ($\epsilon_E \approx 1.07$) is only $\sim$60% larger than at $e = 0.1$ ($\epsilon_E \approx 0.67$).

**RK4 ($k \approx 8.61$):** The extremely steep eccentricity dependence reflects the 4th-order method's sensitivity to the higher derivatives of the gravitational force, which diverge rapidly as $e \to 1$. The periapsis passage concentrates the truncation error into a brief interval of the orbit where $|\dddot{\mathbf{r}}|$ and $|\ddddot{\mathbf{r}}|$ are maximal. The error spans **four orders of magnitude** across the eccentricity range — from $\sim 2.3 \times 10^{-10}$ at $e = 0.1$ to $\sim 2.6 \times 10^{-6}$ at $e = 0.7$.

**Verlet amplitude ($k \approx 4.88$):** The oscillation envelope of the symplectic integrator grows steeply with eccentricity, reflecting the increasing departure of the shadow Hamiltonian from the true Hamiltonian. However, this growth remains **bounded** — there is no secular component — and the exponent is intermediate between Euler and RK4.

---

## 5. The Start Location Amplification Phenomenon

### 5.1 Motivation

A secondary investigation examined whether the orbital phase at which integration begins — periapsis (minimum radius, maximum velocity) versus apoapsis (maximum radius, minimum velocity) — affects the long-term error accumulation. The physical rationale is that periapsis initialization subjects the integrator to the most extreme gradients of $\mathbf{a}(\mathbf{r})$ in its very first time step, potentially seeding a larger initial truncation error.

![Fig. 2: Start Location Effect — Time-resolved fractional energy error at e = 0.7 for all three integrators, comparing pericenter (red) and apocenter (blue) initialization over 100 orbits. Left: Euler shows a clear baseline divergence. Center: RK4 lines overlap perfectly. Right: Verlet oscillation bands are superimposed.](C:/Users/Mosin/.gemini/antigravity/brain/e06af17c-2f24-4eeb-a03d-3200fdd30cc7/Fig2_Start_Location_Effect.png)

### 5.2 Results

**RK4 is insensitive to start location.** The pericenter and apocenter scaling exponents are $k = 8.6051$ and $k = 8.6053$, respectively — a relative difference of $0.002\%$. Point-by-point comparison at $e = 0.7$ yields $\epsilon_E = 2.5896 \times 10^{-6}$ (pericenter) versus $\epsilon_E = 2.5900 \times 10^{-6}$ (apocenter), differing by less than $0.02\%$. The 4th-order Runge-Kutta method possesses sufficient local accuracy to absorb the initial periapsis gradient without propagating a systematic baseline offset.

**Velocity Verlet is insensitive to start location.** The amplitude scaling exponents are $k = 4.8797$ (pericenter) and $k = 4.8789$ (apocenter) — a relative difference of $0.016\%$. The oscillation envelopes are virtually superimposed. Furthermore, the angular momentum conservation is maintained at machine epsilon ($\sim 10^{-15}$) regardless of start location, as expected from the symplectic structure.

**Euler exhibits measurable start-location sensitivity.** The scaling exponent shifts from $k = 0.4435$ at pericenter to $k = 0.3540$ at apocenter — a relative change of **~25%**. At $e = 0.7$, the final error is $\epsilon_E = 1.066$ (pericenter) versus $\epsilon_E = 0.954$ (apocenter), an 11.7% difference. This is consistent with the interpretation that the 1st-order method's large local truncation error at the first periapsis step — where the acceleration magnitude is maximal — seeds a systematically larger drift trajectory that accumulates over the full 100-orbit simulation. When initialized at apoapsis, where the gravitational gradients are weakest, this initial "phase shock" is partially avoided.

### 5.3 Synthesis

The start-location phenomenon obeys a clear hierarchy tied to integrator order and geometric preservation:

| Property | Euler (1st order) | RK4 (4th order) | Verlet (symplectic) |
|---|---|---|---|
| $\Delta k / k$ (peri vs. apo) | ~25% | ~0.002% | ~0.016% |
| Mechanism | 1st-step truncation propagation | Absorbed by local accuracy | Absorbed by symplecticity |
| Conclusion | **Susceptible** | **Immune** | **Immune** |

First-order methods suffer from initial phase-shock — the large truncation error incurred during the first periapsis passage propagates as a permanent baseline offset through the remainder of the integration. Higher-order methods possess sufficient local accuracy to resolve the periapsis dynamics without seeding such an offset. Symplectic methods, by virtue of their geometric preservation properties, are similarly immune: the bounded shadow-Hamiltonian structure prevents any initial perturbation from growing secularly.

---

## 6. Conclusion

This study has demonstrated that the eccentricity-driven secular energy drift in numerical orbit integrators obeys a power-law scaling $\epsilon_E \propto (1-e)^{-k}$, with the exponent $k$ serving as a quantitative signature of the integrator's sensitivity to orbital geometry. The key findings are:

1. **Algorithmic order governs eccentricity sensitivity.** The measured hierarchy $k_{\text{Euler}} \approx 0.44 < k_{\text{Verlet}} \approx 4.88 < k_{\text{RK4}} \approx 8.61$ reflects a fundamental tradeoff: higher-order methods achieve superior absolute accuracy at low eccentricities but suffer more dramatically as $e \to 1$ due to their dependence on higher derivatives of the force field.

2. **Symplectic structure prevents secular drift.** The Velocity Verlet integrator exhibits bounded oscillatory energy errors with zero net secular growth across all eccentricities tested, preserving angular momentum to machine precision. This qualitative advantage persists even though its oscillation amplitude ($k \approx 4.88$) grows more steeply with eccentricity than the Euler secular drift ($k \approx 0.44$).

3. **Start-location sensitivity is a first-order artifact.** Only the Forward Euler method exhibits a measurable dependence of the scaling exponent on initialization phase (~25% shift between periapsis and apoapsis start). The RK4 and Velocity Verlet methods are effectively invariant ($\Delta k / k < 0.02\%$), demonstrating that sufficient local accuracy or geometric preservation renders the integrator immune to initialization-phase effects.

4. **64-bit precision is essential for meaningful benchmarking.** The original 32-bit data campaign produced a false noise floor at $\sim 10^{-7}$ that masked the true RK4 scaling and generated a spurious start-location effect. The upgrade to 64-bit arithmetic lowered detectable errors to $\sim 10^{-10}$, revealing the genuine power-law behavior and correcting a qualitatively incorrect conclusion about start-location dependence.

These results underscore the importance of matching numerical precision to integrator accuracy when conducting benchmarking studies, and they provide a quantitative framework for evaluating integrator suitability in the context of long-duration Keplerian orbit propagation.

---

## 7. Appendix A: Raw Numerical Summaries

> **Note**: The complete numerical data tables for all six configurations (3 methods × 2 start locations) are stored in the corresponding `*_summary.csv` files within the `Version_2/` data directories. These tables will be formatted and attached during final typesetting. The relevant files are:
>
> - `Euler_p/Data/euler_summary.csv`
> - `Euler_Apo/Data/euler_apo_summary.csv`
> - `RK4_p/Data/rk4_summary.csv`
> - `RK4_Apo/Data/rk4_apo_summary.csv`
> - `Verlet/Data/verlet_summary.csv`
> - `Verlet_Apo/Data/verlet_apo_summary.csv`
> - `k_values_summary.csv` (consolidated exponent ledger)

---

*Document compiled from Version_2 data (64-bit, $e \in [0.1, 0.7]$, $\Delta t = 0.00625$, $N_{\text{orb}} = 100$).*
*Computational environment: Python 3 / NumPy (float64). Date: 2 March 2026.*
