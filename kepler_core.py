import numpy as np

MU = 1.0
A = 1.0
TRUE_ENERGY = -MU / (2 * A)
ORBITAL_PERIOD = 2 * np.pi


def acceleration(r):
    r_mag = np.sqrt(r[0]**2 + r[1]**2)
    return -MU * r / r_mag**3


def energy(r, v):
    r_mag = np.sqrt(r[0]**2 + r[1]**2)
    kinetic = 0.5 * np.dot(v, v)
    potential = -MU / r_mag
    return kinetic + potential


def angular_momentum(r, v):
    return r[0]*v[1] - r[1]*v[0]


def fractional_energy_error(E):
    return abs((E - TRUE_ENERGY) / TRUE_ENERGY)


def initial_conditions(e, start="periapsis"):
    if start == "periapsis":
        r_mag = A * (1 - e)
        v_mag = np.sqrt((1 + e) / (1 - e))
    else:
        r_mag = A * (1 + e)
        v_mag = np.sqrt((1 - e) / (1 + e))

    r0 = np.array([r_mag, 0.0], dtype=np.float64)
    v0 = np.array([0.0, v_mag], dtype=np.float64)

    return r0, v0