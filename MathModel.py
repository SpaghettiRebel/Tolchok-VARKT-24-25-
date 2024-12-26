import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import json

# Constants for Kerbin
g = 9.81  # Gravity on Kerbin, m/s^2
rho0 = 0.084  # Air density on Kerbin, kg/m^3
h_scale = 5000  # Corrected scale height for air density, m
A = 6.6  # Cross-sectional area of the rocket, m^2
m_dry = 61700  # Dry mass of the rocket, kg
m_fuel_0 = 71500  # Initial fuel mass, kg
thrust = 1479300  # Maximum thrust, N
fuel_burn_rate = 400  # Basic fuel consumption rate, kg/s


# Functions for simulation
def air_density(h):
    return rho0 * np.exp(-h / h_scale)


def mach_number(v, h):
    temperature = 288.15 - 0.0065 * h  # Temperature in Kelvin at altitude
    sound_speed = 340.29 * (temperature / 288.15) ** 0.5  # Speed of sound
    return v / sound_speed


def drag_force(v, h, angle):
    rho = air_density(h)
    M = mach_number(v, h)

    # Adjust CD based on Mach number and velocity for lower speeds
    if M < 0.5:
        CD = 1.0  # Increased drag at low Mach
    elif M < 1.5:
        CD = 0.6  # Lower drag in subsonic
    elif M < 3:
        CD = 0.4  # Lower drag for supersonic
    else:
        CD = 0.3

    # Effect of angle of attack on drag force
    drag_factor = 1 + 0.5 * np.sin(
        np.radians(angle)
    )  # Stronger modification with angle of attack

    return 0.5 * rho * CD * A * v**2 * drag_factor


def gravity(h):
    """Calculate gravity force based on altitude above Kerbin."""
    radius_k = 600000  # Kerbin's radius
    return g * (radius_k / (radius_k + h)) ** 2


def thrust_force(h, m):
    """Calculate thrust force depending on altitude and remaining mass."""
    return thrust if m > m_dry else thrust * 0.6


def fuel_consumption_rate(m):
    """Calculate fuel consumption rate based on mass."""
    return fuel_burn_rate if m > m_dry else 0


def rocket_pitch_angle(h):
    return (90 * (h - 250)) / 59750


def rocket_dynamics(t, y):
    vy, h, m = y
    angle = rocket_pitch_angle(h)  # Calculate pitch angle based on current altitude
    current_thrust = thrust_force(h, m)
    current_fuel_consumption = fuel_consumption_rate(m)
    drag = drag_force(vy, h, angle)  # Drag force with respect to pitch angle
    dvy_dt = (current_thrust - m * gravity(h) - drag) / m
    dh_dt = vy
    dm_dt = -current_fuel_consumption
    return [dvy_dt, dh_dt, dm_dt]


# Initial conditions and simulation setup
vy0, h0, m0 = 0, 1, m_dry + m_fuel_0
t_span = (0, 129)
t_eval = np.linspace(*t_span, 1000)
solution = solve_ivp(
    rocket_dynamics, t_span, [vy0, h0, m0], t_eval=t_eval, method="RK45"
)

vy, h, m = solution.y


# Load data from JSON
def load_data_from_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    time = [entry["time"] for entry in data]
    altitude = [entry["altitude"] for entry in data]
    velocity = [entry["speed"] for entry in data]
    drag = [entry["aero_force"][1] for entry in data]
    mass = [entry["mass"] for entry in data]  # Assuming mass data exists
    return (time, altitude, velocity, drag, mass)


file_path = "datas/flight_data5m.json"
time_json, altitude_json, velocity_json, drag_json, mass_json = load_data_from_json(
    file_path
)


# Plot results
plt.figure(figsize=(24, 6))

# Altitude plot
plt.subplot(1, 4, 1)
plt.plot(t_eval, h, label="Модель")
plt.plot(time_json, altitude_json, label="KSP", linestyle="--")
plt.xlabel("t, s")
plt.ylabel("h, m")
plt.title("Высота ракеты")
plt.grid(True)
plt.legend()

# Velocity plot
plt.subplot(1, 4, 2)
plt.plot(t_eval, vy, label="Модель")
plt.plot(time_json, velocity_json, label="KSP", linestyle="--")
plt.xlabel("t, s")
plt.ylabel("V, m/s")
plt.title("Скорость ракеты")
plt.grid(True)
plt.legend()

# Mass plot
plt.subplot(1, 4, 4)
plt.plot(t_eval, m - 19500, label="Модель")
if mass_json:
    plt.plot(time_json, mass_json, label="KSP", linestyle="--")
plt.xlabel("t, s")
plt.ylabel("m, kg")
plt.title("Масса ракеты")
plt.grid(True)
plt.legend()

# Plot for the rocket pitch angle
plt.subplot(1, 4, 3)
angles = [rocket_pitch_angle(h_i) for h_i in h]
plt.plot(t_eval, angles, label="Угол наклона ракеты")
plt.xlabel("t, s")
plt.ylabel("Угол наклона, градусы")
plt.title("Изменение угла наклона ракеты")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
