import numpy as np
import matplotlib.pyplot as plt
import math
import json

def plot1():
    with open('flight_data1.json', encoding='UTF-8') as f:
        user = json.load(f)

    time = [user[i]["time"] for i in range(len(user))]
    altitude = [user[i]["altitude"] for i in range(len(user))]

    return [time, altitude]
    

def plot2():
    thrust = 1479300
    diameter = 2.95
    midel_area = math.pi * (diameter / 2) ** 2

    mass_0 = 114055
    G = 6.6743 * 10 ** (- 11)

    M_E = 5.2915158 * (10 ** 22)
    R_E = 600000

    def g(height):
        result = ((G * M_E) / ((R_E + height) ** 2))
        return result

    with open('flight_temperature.json', encoding='UTF-8') as f:
        T = json.load(f)

    def density(height, time):
        temp = 219
        if time <= 103:
            temp = T[time]["air_temperature"]
        h0 = 0.0
        M = 29
        R = 8.314 
        g = 9.81 
        rho0 = 1.2

        rho = (rho0 * np.exp(-height * M * g / (R * temp))) * M / (R * temp)

        return rho


    def calculate_drag_force(atmosphere_density: float, speed: float, midel_area: float):
        c_x_coef = 0.5
        return c_x_coef * (atmosphere_density * (speed ** 2)) / 2 * midel_area



    speed = 0
    height = 0
    current_rocket_mass = mass_0
    fuel_consumption = 479.86

    dt = 1
    theoretical_time = list(range(0, 103, 1))

    theoretical_height = [height]

    for time in theoretical_time:
        atmosphere_density = density(height, time)

        current_rocket_mass = mass_0 - fuel_consumption * time

        current_drag_force = calculate_drag_force(atmosphere_density, speed, midel_area)

        dv = (thrust - current_drag_force - current_rocket_mass * g(height)) / current_rocket_mass * dt

        previous_speed = speed
        speed = previous_speed + dv
        
        height = height + previous_speed * dt
        theoretical_height.append(height)

        
    return [range(len(theoretical_height)), [high for high in theoretical_height]]



plt1 = plot1()
plt2 = plot2()

plt.plot(plt1[0], plt1[1], plt2[0], plt2[1])

plt.xticks(np.arange(0, 103, 20))
plt.yticks(np.arange(0, 32500, 2500))
plt.grid(True)

plt.show()
