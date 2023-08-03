import numpy as np
import matplotlib.pyplot as plt
import random

# SL:
# method motion_model to cal state at x[T+1] do not update pos because can be used as prediction model
# update pose to feed motion_model out put to update vehicel state
# noise function for gps -> x,y , odometry -> v, yaw


def vehicle_update(x, u, params={}):
    """Vehicle dynamics for cruise control system.

    Parameters
    ----------
    x : array
         System state: car velocity in m/s
    u : array
         System input: [throttle, gear, road_slope], where throttle is
         a float between 0 and 1, gear is an integer between 1 and 5,
         and road_slope is in rad.

    Returns
    -------
    float
        Vehicle acceleration

    """
    from math import copysign, sin

    sign = lambda x: copysign(1, x)  # define the sign() function

    # Set up the system parameters
    m = params.get("m", 1600.0)  # vehicle mass, kg
    g = params.get("g", 9.8)  # gravitational constant, m/s^2
    Cr = params.get("Cr", 0.01)  # coefficient of rolling friction
    Cd = params.get("Cd", 0.32)  # drag coefficient
    rho = params.get("rho", 1.3)  # density of air, kg/m^3
    A = params.get("A", 2.4)  # car area, m^2
    alpha = params.get("alpha", [40, 25, 16, 12, 10])  # gear ratio / wheel radius

    # Define variables for vehicle state and inputs
    v = x  # vehicle velocity
    throttle = np.clip(u[0] + random.random() * 0.1, 0, 1)  # vehicle throttle with some error
    gear = u[1]  # vehicle gear
    theta = u[2]  # road slope

    # Force generated by the engine

    omega = alpha[int(gear) - 1] * v  # engine angular speed
    F = alpha[int(gear) - 1] * motor_torque(omega, params) * throttle

    # Disturbance forces
    #
    # The disturbance force Fd has three major components: Fg, the forces due
    # to gravity; Fr, the forces due to rolling friction; and Fa, the
    # aerodynamic drag.

    # Letting the slope of the road be \theta (theta), gravity gives the
    # force Fg = m g sin \theta.

    Fg = m * g * sin(theta)

    # A simple model of rolling friction is Fr = m g Cr sgn(v), where Cr is
    # the coefficient of rolling friction and sgn(v) is the sign of v (±1) or
    # zero if v = 0.

    Fr = m * g * Cr * sign(v)

    # The aerodynamic drag is proportional to the square of the speed: Fa =
    # 1/2 \rho Cd A |v| v, where \rho is the density of air, Cd is the
    # shape-dependent aerodynamic drag coefficient, and A is the frontal area
    # of the car.

    Fa = 1 / 2 * rho * Cd * A * abs(v) * v

    # Final acceleration on the car
    Fd = Fg + Fr + Fa
    dv = (F - Fd) / m

    return dv, throttle


def motor_torque(omega, params={}):
    # Set up the system parameters
    Tm = params.get("Tm", 190.0)  # engine torque constant
    omega_m = params.get("omega_m", 420.0)  # peak engine angular speed
    beta = params.get("beta", 0.4)  # peak engine rolloff

    return np.clip(Tm * (1 - beta * (omega / omega_m - 1) ** 2), 0, None)


def main():
    states = []
    ref = 25
    kp = 0.6
    kd = 0.1
    ki = 0.1
    for i in range(0, 200):
        if i == 0:
            x = 0
            t = 0
            d_err = 0
            i_err = 0
            prev_err = 0
            err = 0
        # ctrl_output = 0.4
        err = ref - x
        d_err = err - prev_err
        ctrl_output = (kp * err) + (ki * i_err) + (kd * d_err)
        acc, thr = vehicle_update(x=x, u=(ctrl_output, 1, 0))
        x = x + acc * (i - t)
        states.append([i, thr, x, acc, err])
        prev_err == err
        i_err += err
        t = i

    arr = np.asarray(states)
    for el in arr:
        if el[2] >= 25:
            print(el)
            break

    plt.plot(arr[:, 0], arr[:, 1], "b.", arr[:, 0], arr[:, 2], "g.", arr[:, 0], arr[:, 4], "r--")
    plt.show()


main()