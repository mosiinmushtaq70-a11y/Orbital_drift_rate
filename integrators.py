import numpy as np
from kepler_core import acceleration


# -----------------------
# Euler
# -----------------------
def euler_integrator(r0, v0, dt, total_time):

    steps = int(total_time / dt)

    r = np.zeros((steps + 1, 2), dtype=np.float64)
    v = np.zeros((steps + 1, 2), dtype=np.float64)
    t = np.zeros(steps + 1, dtype=np.float64)

    r[0] = r0
    v[0] = v0

    for i in range(steps):
        a = acceleration(r[i])
        r[i+1] = r[i] + v[i] * dt
        v[i+1] = v[i] + a * dt
        t[i+1] = t[i] + dt

    return r, v, t


# -----------------------
# RK4
# -----------------------
def rk4_integrator(r0, v0, dt, total_time):

    steps = int(total_time / dt)

    r = np.zeros((steps + 1, 2), dtype=np.float64)
    v = np.zeros((steps + 1, 2), dtype=np.float64)
    t = np.zeros(steps + 1, dtype=np.float64)

    r[0] = r0
    v[0] = v0

    for i in range(steps):

        state_r = r[i]
        state_v = v[i]

        k1_r = state_v
        k1_v = acceleration(state_r)

        k2_r = state_v + 0.5 * dt * k1_v
        k2_v = acceleration(state_r + 0.5 * dt * k1_r)

        k3_r = state_v + 0.5 * dt * k2_v
        k3_v = acceleration(state_r + 0.5 * dt * k2_r)

        k4_r = state_v + dt * k3_v
        k4_v = acceleration(state_r + dt * k3_r)

        r[i+1] = state_r + (dt/6.0) * (k1_r + 2*k2_r + 2*k3_r + k4_r)
        v[i+1] = state_v + (dt/6.0) * (k1_v + 2*k2_v + 2*k3_v + k4_v)
        t[i+1] = t[i] + dt

    return r, v, t


# -----------------------
# Velocity Verlet
# -----------------------
def verlet_integrator(r0, v0, dt, total_time):

    steps = int(total_time / dt)

    r = np.zeros((steps + 1, 2), dtype=np.float64)
    v = np.zeros((steps + 1, 2), dtype=np.float64)
    t = np.zeros(steps + 1, dtype=np.float64)

    r[0] = r0
    v[0] = v0

    a = acceleration(r0)

    for i in range(steps):

        r[i+1] = r[i] + v[i]*dt + 0.5*a*dt**2
        a_new = acceleration(r[i+1])
        v[i+1] = v[i] + 0.5*(a + a_new)*dt
        t[i+1] = t[i] + dt

        a = a_new

    return r, v, t